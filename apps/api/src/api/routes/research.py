"""Research job routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict
from database.connection import get_db_session
from database.repositories import (
    ResearchJobRepository, TaskRepository,
    SourceRepository, EvidenceRepository, ReportRepository,
)
from research.models import ResearchRequest, ResearchJob, ResearchPlan
from research.pipeline import ResearchPipeline
from agents.orchestrator import AgentOrchestrator
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry
from ai.providers.router import ModelRouter
from shared.logging import get_logger

router = APIRouter(prefix="/research", tags=["research"])
logger = get_logger(__name__)


from shared.auth import User
from api.dependencies import get_optional_current_user


# Request/Response models
class ResearchJobCreate(BaseModel):
    question: str
    context: Optional[str] = None
    constraints: list[str] = []
    preferred_sources: list[str] = []
    workspace_id: Optional[UUID] = None
    project_id: Optional[UUID] = None


class ResearchJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    user_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    question: str
    objective: str
    domain: Optional[str]
    scope: Optional[str]
    constraints: list[str]
    expected_output: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    error_message: Optional[str]


class ResearchPlanResponse(BaseModel):
    objective: str
    steps: list[dict]
    expected_outputs: list[str]
    query_tree: Optional[dict] = None
    ambiguity_score: float = 0.0
    inferred_scope: Optional[dict] = None
    replan_count: int = 0
    plan_explanation: str = ""


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    parent_task_id: Optional[UUID] = None
    is_dynamic: bool = False
    depth: int = 0
    type: str
    objective: str
    agent: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    result: Optional[dict]


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    url: Optional[str]
    title: str
    metadata: dict
    retrieved_at: str


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    claim: str
    supporting_text: str
    confidence: float
    source_reliability: float = 1.0
    verification_status: str
    verification_notes: Optional[str] = None
    citation_coordinates: Optional[dict] = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    title: str
    executive_summary: str
    methodology: str
    findings: list[dict]
    evidence: list[dict]
    sources: list[dict]
    contradictions: list[dict] = []
    confidence_score: float = 0.85
    conclusions: list[str]
    limitations: list[str]
    generated_at: str


# Dependencies
async def get_pipeline() -> ResearchPipeline:
    from api.dependencies import (
        get_orchestrator,
        get_agent_registry,
        get_tool_registry,
        get_model_router,
        get_model_gateway,
        get_research_event_bus,
        get_retriever,
    )
    return ResearchPipeline(
        orchestrator=await get_orchestrator(),
        agent_registry=await get_agent_registry(),
        tool_registry=await get_tool_registry(),
        model_router=await get_model_router(),
        model_gateway=await get_model_gateway(),
        event_bus=await get_research_event_bus(),
        retriever=await get_retriever(),
    )


async def run_pipeline_background(pipeline: ResearchPipeline, job_id: str) -> None:
    """Run pipeline in background and handle errors."""
    try:
        await pipeline.run_job(job_id)
    except Exception as e:
        logger.error("Background pipeline execution failed", job_id=job_id, error=str(e))
        # Error is already persisted in run_job via repo.update_status


from shared.security import validate_user_prompt


@router.post("", response_model=ResearchJobResponse, status_code=status.HTTP_201_CREATED)
async def create_research_job(
    request: ResearchJobCreate,
    background_tasks: BackgroundTasks,
    pipeline: ResearchPipeline = Depends(get_pipeline),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Create a new research job and execute it in the background with security validation."""
    try:
        sanitized_question = validate_user_prompt(request.question, min_length=5, max_length=5000)
    except Exception as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )

    user_id_str = str(current_user.id) if current_user and hasattr(current_user, "id") and current_user.id else None
    research_request = ResearchRequest(
        question=sanitized_question,
        context=request.context,
        constraints=request.constraints,
        preferred_sources=request.preferred_sources,
        user_id=user_id_str,
        workspace_id=str(request.workspace_id) if request.workspace_id else None,
        project_id=str(request.project_id) if request.project_id else None,
    )
    
    job = await pipeline.create_job(research_request)
    
    # Schedule background execution
    background_tasks.add_task(run_pipeline_background, pipeline, str(job.id))

    return ResearchJobResponse(
        id=UUID(str(job.id)),
        request_id=UUID(str(job.request_id)),
        user_id=UUID(str(job.user_id)) if getattr(job, "user_id", None) else None,
        workspace_id=UUID(str(job.workspace_id)) if getattr(job, "workspace_id", None) else None,
        project_id=UUID(str(job.project_id)) if getattr(job, "project_id", None) else None,
        question=job.question,
        objective=job.objective,
        domain=job.domain,
        scope=job.scope,
        constraints=job.constraints,
        expected_output=job.expected_output,
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        created_at=job.created_at.isoformat() if hasattr(job.created_at, "isoformat") else str(job.created_at),
        updated_at=job.updated_at.isoformat() if hasattr(job.updated_at, "isoformat") else str(job.updated_at),
        completed_at=job.completed_at.isoformat() if getattr(job, "completed_at", None) and hasattr(job.completed_at, "isoformat") else None,
        error_message=job.error_message,
    )


@router.get("/{job_id}", response_model=ResearchJobResponse)
async def get_research_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get research job by ID."""
    repo = ResearchJobRepository(session)
    job = await repo.get_with_relations(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    return ResearchJobResponse(
        id=job.id,
        request_id=job.request_id,
        question=job.question,
        objective=job.objective,
        domain=job.domain,
        scope=job.scope,
        constraints=job.constraints,
        expected_output=job.expected_output,
        status=job.status,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error_message=job.error_message,
    )


@router.get("/{job_id}/plan", response_model=ResearchPlanResponse)
async def get_research_plan(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get research plan."""
    repo = ResearchJobRepository(session)
    job = await repo.get_with_relations(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    # For now, return a basic plan structure
    # In future, store plan in database
    return ResearchPlanResponse(
        objective=job.objective,
        steps=[],
        expected_outputs=[job.expected_output],
    )


@router.get("/{job_id}/tasks", response_model=list[TaskResponse])
async def get_research_tasks(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get research tasks."""
    repo = ResearchJobRepository(session)
    job = await repo.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    task_repo = TaskRepository(session)
    tasks = await task_repo.get_by_job(job_id)
    
    return [
        TaskResponse(
            id=t.id,
            job_id=t.job_id,
            parent_task_id=getattr(t, "parent_task_id", None),
            is_dynamic=bool(getattr(t, "is_dynamic", False)),
            depth=int(getattr(t, "depth", 0) or 0),
            type=t.type,
            objective=t.objective,
            agent=t.agent,
            status=t.status,
            started_at=t.started_at.isoformat() if t.started_at else None,
            completed_at=t.completed_at.isoformat() if t.completed_at else None,
            error_message=t.error_message,
            result=t.result,
        )
        for t in tasks
    ]


@router.get("/{job_id}/sources", response_model=list[SourceResponse])
async def get_research_sources(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get research sources."""
    repo = ResearchJobRepository(session)
    job = await repo.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    source_repo = SourceRepository(session)
    sources = await source_repo.get_by_job(job_id)
    
    return [
        SourceResponse(
            id=s.id,
            type=s.type,
            url=s.url,
            title=s.title,
            metadata=s.metadata,
            retrieved_at=s.retrieved_at.isoformat(),
        )
        for s in sources
    ]


@router.get("/{job_id}/evidence", response_model=list[EvidenceResponse])
async def get_research_evidence(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get research evidence."""
    repo = ResearchJobRepository(session)
    job = await repo.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    evidence_repo = EvidenceRepository(session)
    evidence = await evidence_repo.get_by_job(job_id)
    
    return [
        EvidenceResponse(
            id=e.id,
            source_id=e.source_id,
            claim=e.claim,
            supporting_text=e.supporting_text,
            confidence=e.confidence,
            source_reliability=getattr(e, "source_reliability", 1.0) or 1.0,
            verification_status=e.verification_status,
            verification_notes=e.verification_notes,
            citation_coordinates=getattr(e, "citation_coordinates", {}) or {},
        )
        for e in evidence
    ]


@router.get("/{job_id}/report", response_model=ReportResponse)
async def get_research_report(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get research report."""
    repo = ResearchJobRepository(session)
    job = await repo.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    report_repo = ReportRepository(session)
    report = await report_repo.get_by_job(job_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(
        id=report.id,
        job_id=report.job_id,
        title=report.title,
        executive_summary=report.executive_summary or "",
        methodology=report.methodology or "",
        findings=report.findings,
        evidence=report.evidence_ids,
        sources=report.source_ids,
        contradictions=getattr(report, "contradictions", []) or [],
        confidence_score=getattr(report, "confidence_score", 0.85) or 0.85,
        conclusions=report.conclusions,
        limitations=report.limitations,
        generated_at=report.generated_at.isoformat(),
    )


@router.get("", response_model=list[ResearchJobResponse])
async def list_research_jobs(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    workspace_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """List research jobs."""
    repo = ResearchJobRepository(session)
    
    job_status = None
    if status:
        try:
            from shared.types import JobStatus
            job_status = JobStatus(status)
        except ValueError:
            pass
    
    jobs = await repo.list_jobs(
        limit=limit,
        offset=offset,
        status=job_status,
        workspace_id=workspace_id,
        project_id=project_id,
    )
    
    return [
        ResearchJobResponse(
            id=j.id,
            request_id=j.request_id,
            user_id=j.user_id,
            workspace_id=j.workspace_id,
            project_id=j.project_id,
            question=j.question,
            objective=j.objective,
            domain=j.domain,
            scope=j.scope,
            constraints=j.constraints,
            expected_output=j.expected_output,
            status=j.status,
            created_at=j.created_at.isoformat(),
            updated_at=j.updated_at.isoformat(),
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
            error_message=j.error_message,
        )
        for j in jobs
    ]
