"""Research job routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database.connection import get_session
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


# Request/Response models
class ResearchJobCreate(BaseModel):
    question: str
    context: Optional[str] = None
    constraints: list[str] = []
    preferred_sources: list[str] = []


class ResearchJobResponse(BaseModel):
    id: UUID
    request_id: UUID
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
    
    class Config:
        from_attributes = True


class ResearchPlanResponse(BaseModel):
    objective: str
    steps: list[dict]
    expected_outputs: list[str]


class TaskResponse(BaseModel):
    id: UUID
    job_id: UUID
    type: str
    objective: str
    agent: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    result: Optional[dict]
    
    class Config:
        from_attributes = True


class SourceResponse(BaseModel):
    id: UUID
    type: str
    url: Optional[str]
    title: str
    metadata: dict
    retrieved_at: str
    
    class Config:
        from_attributes = True


class EvidenceResponse(BaseModel):
    id: UUID
    source_id: UUID
    claim: str
    supporting_text: str
    confidence: float
    verification_status: str
    verification_notes: Optional[str]
    
    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: UUID
    job_id: UUID
    title: str
    executive_summary: str
    methodology: str
    findings: list[dict]
    evidence: list[dict]
    sources: list[dict]
    conclusions: list[str]
    limitations: list[str]
    generated_at: str
    
    class Config:
        from_attributes = True


# Dependencies
async def get_pipeline() -> ResearchPipeline:
    from api.dependencies import get_orchestrator, get_agent_registry, get_tool_registry, get_model_router
    return ResearchPipeline(
        orchestrator=await get_orchestrator(),
        agent_registry=await get_agent_registry(),
        tool_registry=await get_tool_registry(),
        model_router=await get_model_router(),
    )


async def run_pipeline_background(pipeline: ResearchPipeline, job_id: str) -> None:
    """Run pipeline in background and handle errors."""
    try:
        await pipeline.run_job(job_id)
    except Exception as e:
        logger.error("Background pipeline execution failed", job_id=job_id, error=str(e))
        # Error is already persisted in run_job via repo.update_status


@router.post("", response_model=ResearchJobResponse, status_code=status.HTTP_201_CREATED)
async def create_research_job(
    request: ResearchJobCreate,
    background_tasks: BackgroundTasks,
    pipeline: ResearchPipeline = Depends(get_pipeline),
):
    """Create a new research job and execute it in the background."""
    research_request = ResearchRequest(
        question=request.question,
        context=request.context,
        constraints=request.constraints,
        preferred_sources=request.preferred_sources,
    )
    
    job = await pipeline.create_job(research_request)
    
    # Schedule background execution
    background_tasks.add_task(run_pipeline_background, pipeline, str(job.id))

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


@router.get("/{job_id}", response_model=ResearchJobResponse)
async def get_research_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
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
    session: AsyncSession = Depends(get_session),
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
    session: AsyncSession = Depends(get_session),
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
    session: AsyncSession = Depends(get_session),
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
    session: AsyncSession = Depends(get_session),
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
            verification_status=e.verification_status,
            verification_notes=e.verification_notes,
        )
        for e in evidence
    ]


@router.get("/{job_id}/report", response_model=ReportResponse)
async def get_research_report(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
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
        conclusions=report.conclusions,
        limitations=report.limitations,
        generated_at=report.generated_at.isoformat(),
    )


@router.get("", response_model=list[ResearchJobResponse])
async def list_research_jobs(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
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
    
    jobs = await repo.list_jobs(limit=limit, offset=offset, status=job_status)
    
    return [
        ResearchJobResponse(
            id=j.id,
            request_id=j.request_id,
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