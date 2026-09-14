"""Production Infrastructure, Distributed Task Queue & Object Storage REST API (Phase 24)."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_optional_current_user
from database.repositories.infrastructure_repo import InfrastructureRepository
from database.repositories.workspace_repo import WorkspaceRepository
from research.workers.task_queue import (
    AsyncTaskQueue,
    QueuedTask,
    QueuePriority,
    WorkerNode,
    global_task_queue,
)
from shared.auth import User
from shared.logging import get_logger
from shared.storage import ObjectStorageClient

router = APIRouter(prefix="/system", tags=["production-infrastructure"])
logger = get_logger(__name__)
storage_client = ObjectStorageClient()


class WorkerHeartbeatRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    worker_id: str
    hostname: str = "node.cluster.local"
    concurrency: int = 4
    active_tasks: List[str] = Field(default_factory=list)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "HEALTHY"


class EnqueueTaskRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    task_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: QueuePriority = QueuePriority.DEFAULT
    job_id: Optional[str] = None
    max_retries: int = 3


class PresignedUrlRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    object_key: str
    bucket: Optional[str] = None
    operation: str = Field("get_object", description="get_object, put_object")
    expires_in_seconds: int = Field(3600, ge=60, le=86400)


class CatalogStorageObjectRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    bucket: str
    object_key: str
    size_bytes: int
    etag: str
    md5_hash: str
    sha256_hash: str
    content_type: str = "application/octet-stream"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    workspace_id: Optional[UUID] = None


@router.get("/workers", response_model=List[Dict[str, Any]])
async def list_worker_nodes(
    include_offline: bool = Query(True),
    session: AsyncSession = Depends(get_db_session),
):
    """List cluster worker nodes, CPU/Memory telemetry, and active task loads."""
    repo = InfrastructureRepository(session)
    await repo.sweep_stale_workers(timeout_seconds=60)
    workers = await repo.list_workers(include_offline=include_offline)
    return [w.to_dict() for w in workers]


@router.post("/workers/heartbeat", response_model=Dict[str, Any])
async def record_worker_heartbeat(
    payload: WorkerHeartbeatRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Register or pulse a background worker heartbeat."""
    repo = InfrastructureRepository(session)
    worker = await repo.register_or_heartbeat_worker(
        worker_id=payload.worker_id,
        hostname=payload.hostname,
        concurrency=payload.concurrency,
        active_tasks=payload.active_tasks,
        cpu_percent=payload.cpu_percent,
        memory_mb=payload.memory_mb,
        status=payload.status,
    )
    return worker.to_dict()


@router.get("/queue/status", response_model=Dict[str, Any])
async def get_queue_status():
    """Retrieve real-time task queue depth and state distribution."""
    metrics = await global_task_queue.get_queue_metrics()
    return metrics


@router.post("/queue/tasks", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def enqueue_task(payload: EnqueueTaskRequest):
    """Enqueue an asynchronous task into the distributed priority queue."""
    task = await global_task_queue.enqueue(
        task_type=payload.task_type,
        payload=payload.payload,
        priority=payload.priority,
        job_id=payload.job_id,
        max_retries=payload.max_retries,
    )
    return task.to_dict()


@router.get("/queue/tasks/{id}", response_model=Dict[str, Any])
async def get_queued_task(id: str):
    """Get status of an enqueued task."""
    task = await global_task_queue.get_task(id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{id}' not found")
    return task.to_dict()


@router.get("/storage/objects", response_model=List[Dict[str, Any]])
async def list_storage_objects(
    workspace_id: Optional[UUID] = Query(None),
    bucket: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """List cataloged S3/MinIO/Local blob objects."""
    repo = InfrastructureRepository(session)
    objects = await repo.list_storage_objects(
        workspace_id=workspace_id,
        bucket=bucket,
        limit=limit,
        offset=offset,
    )
    return [o.to_dict() for o in objects]


@router.post("/storage/objects", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def catalog_storage_object(
    payload: CatalogStorageObjectRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Register stored object metadata in database catalog."""
    repo = InfrastructureRepository(session)
    actor_id = None
    if current_user and hasattr(current_user, "id") and current_user.id:
        try:
            actor_id = UUID(str(current_user.id)) if not isinstance(current_user.id, UUID) else current_user.id
        except Exception:
            actor_id = None

    obj = await repo.record_storage_object(
        bucket=payload.bucket,
        object_key=payload.object_key,
        size_bytes=payload.size_bytes,
        etag=payload.etag,
        md5_hash=payload.md5_hash,
        sha256_hash=payload.sha256_hash,
        content_type=payload.content_type,
        metadata=payload.metadata,
        workspace_id=payload.workspace_id,
        uploader_id=actor_id,
    )
    return obj.to_dict()


@router.post("/storage/presigned-url", response_model=Dict[str, Any])
async def generate_presigned_url(payload: PresignedUrlRequest):
    """Generate a presigned upload or download URL."""
    return storage_client.generate_presigned_url(
        object_key=payload.object_key,
        bucket=payload.bucket,
        operation=payload.operation,
        expires_in_seconds=payload.expires_in_seconds,
    )


@router.get("/storage/usage", response_model=Dict[str, Any])
async def get_storage_usage(
    workspace_id: Optional[UUID] = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve aggregate storage usage and bucket statistics."""
    repo = InfrastructureRepository(session)
    db_usage = await repo.get_storage_usage_summary(workspace_id)
    bucket_metrics = storage_client.get_bucket_metrics()
    return {
        "database_catalog_summary": db_usage,
        "local_storage_metrics": bucket_metrics,
    }


@router.post("/seed", response_model=Dict[str, Any])
async def seed_demo_environment(
    session: AsyncSession = Depends(get_db_session),
):
    """Populates the database with realistic demo research data across all 34 phases."""
    from src.scripts.seed_demo_data import seed_all_demo_data
    result = await seed_all_demo_data(session)
    return result

