"""
Research Automation, Scheduled Sweeps, and Alerting API (Phase 26).
Enables recurring topic sweeps, autonomous diffing, and webhook notifications.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_optional_current_user
from database.repositories.automation_repo import AutomationRepository
from database.repositories.user_repo import UserRepository
from database.repositories.workspace_repo import WorkspaceRepository
from research.automation.engine import ResearchAutomationEngine, compute_next_run
from shared.auth import User
from shared.logging import get_logger

router = APIRouter(prefix="/automation", tags=["research-automation"])
logger = get_logger(__name__)


# ----------------------------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------------------------

class CreateScheduleRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    title: str = Field(..., min_length=2, max_length=255)
    query_topic: str = Field(..., min_length=3)
    cron_expression: str = Field("0 9 * * 1-5", description="Cron or interval: @daily, @hourly, every_6h, */30 * * * *")
    routing_profile: str = Field("balanced", description="balanced, speed_maximized, cost_minimized, quality_maximized")
    source_types: Optional[List[str]] = Field(default=["web", "academic", "knowledge_vault"])
    novelty_threshold: float = Field(0.30, ge=0.0, le=1.0)
    confidence_threshold: float = Field(0.85, ge=0.0, le=1.0)
    contradiction_alert: bool = True
    webhook_url: Optional[str] = None
    email_notifications: Optional[List[str]] = Field(default_factory=list)
    workspace_id: Optional[UUID] = None


class UpdateScheduleRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    title: Optional[str] = Field(None, min_length=2, max_length=255)
    query_topic: Optional[str] = None
    cron_expression: Optional[str] = None
    routing_profile: Optional[str] = None
    source_types: Optional[List[str]] = None
    novelty_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    contradiction_alert: Optional[bool] = None
    webhook_url: Optional[str] = None
    email_notifications: Optional[List[str]] = None
    status: Optional[str] = None


class TriggerSweepRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    simulated_findings: Optional[List[Dict[str, Any]]] = None
    contradictions: Optional[List[Dict[str, Any]]] = None


# ----------------------------------------------------------------------
# Helper Dependencies
# ----------------------------------------------------------------------

async def _resolve_user_id(
    current_user: Optional[User],
    db_session: AsyncSession,
) -> UUID:
    """Resolve a valid database user ID from current JWT context or fallback user."""
    user_repo = UserRepository(db_session)
    if current_user:
        db_user = await user_repo.get_by_email(current_user.email)
        if db_user:
            return db_user.id

    default_user = await user_repo.get_by_username("system_researcher")
    if not default_user:
        default_user = await user_repo.create(
            username="system_researcher",
            email="researcher@system.local",
            password_hash="system_managed_automation",
            role="Researcher",
        )
    return default_user.id


# ----------------------------------------------------------------------
# API Endpoints
# ----------------------------------------------------------------------

@router.get("/schedules", response_model=List[Dict[str, Any]])
async def list_schedules(
    workspace_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """List scheduled research sweeps for workspace or user."""
    repo = AutomationRepository(db_session)
    schedules = await repo.list_schedules(
        workspace_id=workspace_id, status=status, limit=limit
    )
    return [s.to_dict() for s in schedules]


@router.post("/schedules", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_schedule(
    request: CreateScheduleRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Create a new recurring scheduled research sweep."""
    user_id = await _resolve_user_id(current_user, db_session)
    repo = AutomationRepository(db_session)

    # Compute next run time
    next_run = compute_next_run(request.cron_expression)

    schedule = await repo.create_schedule(
        user_id=user_id,
        title=request.title,
        query_topic=request.query_topic,
        cron_expression=request.cron_expression,
        routing_profile=request.routing_profile,
        source_types=request.source_types,
        novelty_threshold=request.novelty_threshold,
        confidence_threshold=request.confidence_threshold,
        contradiction_alert=request.contradiction_alert,
        webhook_url=request.webhook_url,
        email_notifications=request.email_notifications,
        workspace_id=request.workspace_id,
        next_run_at=next_run,
    )

    logger.info(
        "research_schedule_created",
        schedule_id=str(schedule.id),
        title=schedule.title,
        cron=schedule.cron_expression,
    )
    return schedule.to_dict()


@router.get("/schedules/{schedule_id}", response_model=Dict[str, Any])
async def get_schedule(
    schedule_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve details for a specific research schedule."""
    repo = AutomationRepository(db_session)
    schedule = await repo.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled research job not found",
        )
    return schedule.to_dict()


@router.patch("/schedules/{schedule_id}", response_model=Dict[str, Any])
async def update_schedule(
    schedule_id: UUID,
    request: UpdateScheduleRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Update fields of an existing research schedule."""
    repo = AutomationRepository(db_session)
    updates = request.model_dump(exclude_unset=True)
    if not updates:
        schedule = await repo.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule.to_dict()

    schedule = await repo.update_schedule(schedule_id, **updates)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule.to_dict()


@router.patch("/schedules/{schedule_id}/pause", response_model=Dict[str, Any])
async def pause_schedule(
    schedule_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Pause an active scheduled sweep."""
    repo = AutomationRepository(db_session)
    schedule = await repo.pause_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule.to_dict()


@router.patch("/schedules/{schedule_id}/resume", response_model=Dict[str, Any])
async def resume_schedule(
    schedule_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Resume a paused scheduled sweep."""
    repo = AutomationRepository(db_session)
    schedule = await repo.resume_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule.to_dict()


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_200_OK)
async def delete_schedule(
    schedule_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Delete a scheduled sweep job and associated sweep records."""
    repo = AutomationRepository(db_session)
    success = await repo.delete_schedule(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Scheduled research successfully deleted", "schedule_id": str(schedule_id)}


@router.post("/schedules/{schedule_id}/trigger", response_model=Dict[str, Any])
async def trigger_sweep_now(
    schedule_id: UUID,
    payload: Optional[TriggerSweepRequest] = None,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Manually trigger an immediate execution sweep pass."""
    repo = AutomationRepository(db_session)
    schedule = await repo.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    engine = ResearchAutomationEngine(repo)
    simulated_findings = payload.simulated_findings if payload else None
    contradictions = payload.contradictions if payload else None

    sweep_result = await engine.execute_sweep_run(
        schedule_id=schedule_id,
        generated_findings=simulated_findings,
        contradictions=contradictions,
        duration_ms=1450.0,
    )

    logger.info(
        "manual_sweep_executed",
        schedule_id=str(schedule_id),
        status=sweep_result.status,
        novelty_score=sweep_result.novelty_score,
        alert_dispatched=sweep_result.alert_dispatched,
    )
    return sweep_result.to_dict()


@router.get("/schedules/{schedule_id}/sweeps", response_model=List[Dict[str, Any]])
async def list_schedule_sweeps(
    schedule_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Query historical sweep execution records for a schedule."""
    repo = AutomationRepository(db_session)
    sweeps = await repo.list_sweep_results(schedule_id=schedule_id, limit=limit)
    return [s.to_dict() for s in sweeps]


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def list_alerts(
    workspace_id: Optional[UUID] = Query(None),
    schedule_id: Optional[UUID] = Query(None),
    is_acknowledged: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Query generated automation alerts."""
    repo = AutomationRepository(db_session)
    alerts = await repo.list_alerts(
        workspace_id=workspace_id,
        schedule_id=schedule_id,
        is_acknowledged=is_acknowledged,
        limit=limit,
    )
    return [a.to_dict() for a in alerts]


@router.patch("/alerts/{alert_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_alert(
    alert_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Mark an alert notification as acknowledged."""
    repo = AutomationRepository(db_session)
    alert = await repo.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert.to_dict()


@router.get("/metrics", response_model=Dict[str, Any])
async def get_automation_metrics(
    workspace_id: Optional[UUID] = Query(None),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve aggregate automation metrics (schedules, sweeps, alerts)."""
    repo = AutomationRepository(db_session)
    metrics = await repo.get_automation_metrics(workspace_id=workspace_id)
    return metrics
