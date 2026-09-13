"""
Developer Platform & Public REST Gateway API (Phase 25).
Provides API key provisioning, rate limiting, and programmatic research/retrieval endpoints.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_optional_current_user
from database.models.api_key import DBApiKey
from database.models.document import Document
from database.models.research_job import ResearchJob
from database.repositories.api_key_repo import ApiKeyRepository
from database.repositories.document_repo import DocumentRepository
from database.repositories.report_repo import ReportRepository
from database.repositories.research_job_repo import ResearchJobRepository, TaskRepository
from database.repositories.workspace_repo import WorkspaceRepository
from research.models import ResearchRequest, ResearchJob as ResearchJobSchema
from research.pipeline import ResearchPipeline
from shared.auth import User
from shared.logging import get_logger
from shared.types import JobStatus

router = APIRouter(prefix="/developer", tags=["developer-platform"])
logger = get_logger(__name__)


# ----------------------------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------------------------

class CreateApiKeyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., min_length=1, max_length=100)
    scopes: Optional[List[str]] = Field(
        default=["research:read", "research:write", "documents:read", "documents:write", "memory:read", "graph:read"]
    )
    rate_limit_tier: str = Field("free", description="free (60 rpm), pro (300 rpm), enterprise (1200 rpm)")
    workspace_id: Optional[UUID] = None
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class DeveloperResearchRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    question: str = Field(..., min_length=3)
    context: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    routing_profile: Optional[str] = "balanced"
    workspace_id: Optional[UUID] = None
    project_id: Optional[UUID] = None


class DeveloperDocumentIngestRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10)
    source_type: str = "text"
    workspace_id: Optional[UUID] = None


# ----------------------------------------------------------------------
# Developer API Key Authentication Dependency
# ----------------------------------------------------------------------

async def get_developer_api_auth(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_db_session),
) -> DBApiKey:
    """
    Authenticates developer requests via X-API-Key or Bearer token.
    Applies sliding window rate limiting.
    """
    raw_key: Optional[str] = None
    if x_api_key:
        raw_key = x_api_key.strip()
    elif authorization and authorization.startswith("Bearer amrp_"):
        raw_key = authorization.replace("Bearer ", "").strip()

    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Developer API Key. Provide via 'X-API-Key' header or 'Authorization: Bearer <key>'.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    api_key_repo = ApiKeyRepository()
    key_record = await api_key_repo.authenticate_api_key(session, raw_key)
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Developer API Key.",
        )

    # Check Rate Limit
    allowed, remaining, retry_after = ApiKeyRepository.check_rate_limit(
        str(key_record.id), key_record.rate_limit_rpm
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for tier '{key_record.rate_limit_tier}'. Limit: {key_record.rate_limit_rpm} rpm.",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(key_record.rate_limit_rpm),
                "X-RateLimit-Remaining": "0",
            },
        )

    # Attach remaining count to request state
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_rpm = key_record.rate_limit_rpm

    return key_record


# ----------------------------------------------------------------------
# API Key Management Routes (User JWT Auth)
# ----------------------------------------------------------------------

@router.post("/keys", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_developer_api_key(
    payload: CreateApiKeyRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Generate a new Developer API Key.
    Returns the persistent key metadata and the raw key string (shown only once).
    """
    user_id = current_user.id if current_user else uuid.UUID("00000000-0000-0000-0000-000000000001")
    repo = ApiKeyRepository()

    key_record, raw_key = await repo.create_api_key(
        session=session,
        user_id=user_id,
        name=payload.name,
        scopes=payload.scopes,
        rate_limit_tier=payload.rate_limit_tier,
        workspace_id=payload.workspace_id,
        expires_in_days=payload.expires_in_days,
    )

    return {
        "message": "Developer API Key created successfully. Store the secret_key securely; it will not be shown again.",
        "api_key": key_record.to_dict(),
        "secret_key": raw_key,
    }


@router.get("/keys", response_model=List[Dict[str, Any]])
async def list_developer_api_keys(
    workspace_id: Optional[UUID] = Query(None),
    current_user: Optional[User] = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """List all Developer API Keys created by current user/workspace."""
    user_id = current_user.id if current_user else uuid.UUID("00000000-0000-0000-0000-000000000001")
    repo = ApiKeyRepository()
    keys = await repo.list_api_keys(session, user_id=user_id, workspace_id=workspace_id)
    return [k.to_dict() for k in keys]


@router.patch("/keys/{key_id}/revoke", response_model=Dict[str, Any])
async def revoke_developer_api_key(
    key_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Revoke (deactivate) a Developer API Key."""
    user_id = current_user.id if current_user else uuid.UUID("00000000-0000-0000-0000-000000000001")
    repo = ApiKeyRepository()
    success = await repo.revoke_api_key(session, key_id=key_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found or unauthorized.")
    return {"message": "API Key revoked successfully.", "key_id": str(key_id)}


@router.delete("/keys/{key_id}", response_model=Dict[str, Any])
async def delete_developer_api_key(
    key_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Permanently delete a Developer API Key."""
    user_id = current_user.id if current_user else uuid.UUID("00000000-0000-0000-0000-000000000001")
    repo = ApiKeyRepository()
    success = await repo.delete_api_key(session, key_id=key_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found or unauthorized.")
    return {"message": "API Key deleted permanently.", "key_id": str(key_id)}


# ----------------------------------------------------------------------
# Public Programmatic Developer Endpoints (API Key Auth)
# ----------------------------------------------------------------------

@router.post("/research", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def create_developer_research_job(
    payload: DeveloperResearchRequest,
    background_tasks: BackgroundTasks,
    auth_key: DBApiKey = Depends(get_developer_api_auth),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Programmatic endpoint to trigger autonomous multi-agent research.
    Requires scope: 'research:write'.
    """
    if "research:write" not in (auth_key.scopes or []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scope 'research:write' is required for this endpoint.",
        )

    job_repo = ResearchJobRepository(session)
    job_id = uuid.uuid4()
    request_id = uuid.uuid4()

    workspace_id = payload.workspace_id or auth_key.workspace_id
    project_id = payload.project_id

    # Create job in database
    db_job = ResearchJob(
        id=job_id,
        request_id=request_id,
        user_id=auth_key.user_id,
        workspace_id=workspace_id,
        project_id=project_id,
        question=payload.question,
        objective=payload.question,
        constraints=payload.constraints,
        expected_output="comprehensive_report",
        status=JobStatus.PENDING.value,
    )
    await job_repo.create(db_job)
    await session.commit()

    return {
        "job_id": str(job_id),
        "request_id": str(request_id),
        "status": "queued",
        "question": payload.question,
        "workspace_id": str(workspace_id) if workspace_id else None,
        "created_at": db_job.created_at.isoformat() if db_job.created_at else None,
        "poll_url": f"/api/v1/developer/research/{job_id}",
    }


@router.get("/research/{job_id}", response_model=Dict[str, Any])
async def get_developer_research_job(
    job_id: UUID,
    auth_key: DBApiKey = Depends(get_developer_api_auth),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Programmatic endpoint to poll research job status, tasks, and report synthesis.
    Requires scope: 'research:read'.
    """
    if "research:read" not in (auth_key.scopes or []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scope 'research:read' is required for this endpoint.",
        )

    job_repo = ResearchJobRepository(session)
    task_repo = TaskRepository(session)
    report_repo = ReportRepository(session)

    db_job = await job_repo.get(job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Research job not found.")

    tasks = await task_repo.get_by_job(job_id)
    report = await report_repo.get_by_job(job_id)

    return {
        "job_id": str(db_job.id),
        "status": db_job.status,
        "question": db_job.question,
        "objective": db_job.objective,
        "created_at": db_job.created_at.isoformat() if db_job.created_at else None,
        "updated_at": db_job.updated_at.isoformat() if db_job.updated_at else None,
        "completed_at": db_job.completed_at.isoformat() if db_job.completed_at else None,
        "tasks": [
            {
                "task_id": str(t.id),
                "title": t.title,
                "status": t.status,
                "assigned_agent": t.assigned_agent,
            }
            for t in tasks
        ],
        "report": {
            "report_id": str(report.id),
            "title": report.title,
            "summary": report.summary,
            "content": report.content,
        } if report else None,
    }


@router.get("/research", response_model=List[Dict[str, Any]])
async def list_developer_research_jobs(
    limit: int = Query(20, ge=1, le=100),
    auth_key: DBApiKey = Depends(get_developer_api_auth),
    session: AsyncSession = Depends(get_db_session),
):
    """
    List research jobs accessible to this API key.
    Requires scope: 'research:read'.
    """
    if "research:read" not in (auth_key.scopes or []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scope 'research:read' is required for this endpoint.",
        )

    job_repo = ResearchJobRepository(session)
    jobs = await job_repo.list_jobs(user_id=auth_key.user_id, limit=limit)
    return [
        {
            "job_id": str(j.id),
            "question": j.question,
            "status": j.status,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.post("/documents", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def ingest_developer_document(
    payload: DeveloperDocumentIngestRequest,
    auth_key: DBApiKey = Depends(get_developer_api_auth),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Programmatic endpoint to ingest text documents into knowledge base.
    Requires scope: 'documents:write'.
    """
    if "documents:write" not in (auth_key.scopes or []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scope 'documents:write' is required for this endpoint.",
        )

    doc_repo = DocumentRepository(session)
    doc_id = uuid.uuid4()
    workspace_id = payload.workspace_id or auth_key.workspace_id

    doc = Document(
        id=doc_id,
        user_id=auth_key.user_id,
        workspace_id=workspace_id,
        filename=payload.title,
        mime_type="text/plain",
        content=payload.content,
        status="ready",
    )
    await doc_repo.create(doc)
    await session.commit()

    return {
        "document_id": str(doc.id),
        "title": doc.filename,
        "status": doc.status,
        "workspace_id": str(workspace_id) if workspace_id else None,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }


@router.get("/usage", response_model=Dict[str, Any])
async def get_developer_api_usage(
    request: Request,
    auth_key: DBApiKey = Depends(get_developer_api_auth),
):
    """
    Returns current API key telemetry, rate limit quotas, and remaining calls.
    """
    remaining = getattr(request.state, "rate_limit_remaining", auth_key.rate_limit_rpm)
    return {
        "key_id": str(auth_key.id),
        "name": auth_key.name,
        "tier": auth_key.rate_limit_tier,
        "rate_limit_rpm": auth_key.rate_limit_rpm,
        "rate_limit_remaining": remaining,
        "scopes": auth_key.scopes,
        "last_used_at": auth_key.last_used_at.isoformat() if auth_key.last_used_at else None,
    }
