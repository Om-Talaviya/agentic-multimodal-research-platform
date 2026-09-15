"""Agent Evaluation and Observability REST routes (Phase 22)."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ai.eval.agent_evaluator import (
    AgentEvaluationScorecard,
    AgentEvaluator,
    AgentStepTelemetry,
)
from api.dependencies import get_db_session, get_optional_current_user
from database.repositories.agent_evaluation_repo import AgentEvaluationRepository
from shared.auth import User
from shared.logging import get_logger

router = APIRouter(prefix="/agents", tags=["agent-evaluations"])
logger = get_logger(__name__)


class RunAgentEvaluationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    agent_name: str = "ResearchPipeline"
    job_id: Optional[UUID] = None
    research_objective: Optional[str] = "Autonomous multi-modal research investigation"
    plan_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    step_telemetry: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_items: List[Dict[str, Any]] = Field(default_factory=list)
    report_text: str = ""
    claims: List[str] = Field(default_factory=list)
    execution_time_ms: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0


@router.post("/evaluate", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def evaluate_agent_execution(
    payload: RunAgentEvaluationRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Calculate and persist evaluation scorecard for an agent run or research job."""
    # Convert step dicts to telemetry objects
    telemetry_objects = [
        AgentStepTelemetry(
            step_index=s.get("step_index", i),
            agent_type=s.get("agent_type", payload.agent_name),
            action_type=s.get("action_type", "execute"),
            tool_name=s.get("tool_name"),
            tool_args=s.get("tool_args", {}),
            tool_output_length=s.get("tool_output_length", 0),
            success=s.get("success", True),
            error_message=s.get("error_message"),
            latency_ms=s.get("latency_ms", 0),
            tokens_consumed=s.get("tokens_consumed", 0),
        )
        for i, s in enumerate(payload.step_telemetry, start=1)
    ]

    scorecard: AgentEvaluationScorecard = AgentEvaluator.evaluate_job_execution(
        job_id=str(payload.job_id) if payload.job_id else "",
        agent_name=payload.agent_name,
        plan_tasks=payload.plan_tasks,
        research_objective=payload.research_objective or "",
        step_telemetry=telemetry_objects,
        evidence_items=payload.evidence_items,
        report_text=payload.report_text,
        claims=payload.claims,
        execution_time_ms=payload.execution_time_ms,
        total_tokens=payload.total_tokens,
        cost_usd=payload.cost_usd,
    )

    repo = AgentEvaluationRepository(session)
    user_uuid = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None

    saved_eval = await repo.create_evaluation(
        agent_name=scorecard.agent_name,
        total_steps=scorecard.total_steps,
        successful_steps=scorecard.successful_steps,
        failed_steps=scorecard.failed_steps,
        plan_precision=scorecard.plan_precision,
        tool_accuracy=scorecard.tool_accuracy,
        evidence_coverage=scorecard.evidence_coverage,
        hallucination_rate=scorecard.hallucination_rate,
        synthesis_fidelity=scorecard.synthesis_fidelity,
        overall_score=scorecard.overall_score,
        execution_time_ms=scorecard.execution_time_ms,
        total_tokens=scorecard.total_tokens,
        estimated_cost_usd=scorecard.estimated_cost_usd,
        findings_audit=scorecard.findings_audit,
        job_id=payload.job_id,
        evaluated_by=user_uuid,
        step_telemetry=[s.model_dump() for s in telemetry_objects],
    )

    return saved_eval.to_dict()


@router.get("/evaluations", response_model=List[Dict[str, Any]])
async def list_agent_evaluations(
    agent_name: Optional[str] = Query(None),
    job_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical agent evaluations."""
    repo = AgentEvaluationRepository(session)
    evals = await repo.list_evaluations(
        agent_name=agent_name,
        job_id=job_id,
        limit=limit,
        offset=offset,
    )
    return [e.to_dict() for e in evals]


@router.get("/evaluations/{id}", response_model=Dict[str, Any])
async def get_agent_evaluation_detail(
    id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get detailed agent evaluation scorecard with step telemetry."""
    repo = AgentEvaluationRepository(session)
    eval_record = await repo.get_evaluation_by_id(id)
    if not eval_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent evaluation '{id}' not found",
        )

    res = eval_record.to_dict()
    res["steps"] = [s.to_dict() for s in eval_record.steps]
    return res


@router.delete("/evaluations/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_evaluation(
    id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete an agent evaluation record."""
    repo = AgentEvaluationRepository(session)
    deleted = await repo.delete_evaluation(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent evaluation '{id}' not found",
        )
    return None


@router.get("/metrics/summary", response_model=Dict[str, Any])
async def get_agent_metrics_summary(
    session: AsyncSession = Depends(get_db_session),
):
    """Aggregate system-wide agent quality, hallucination rate, and execution efficiency."""
    repo = AgentEvaluationRepository(session)
    return await repo.get_agent_metrics_summary()
