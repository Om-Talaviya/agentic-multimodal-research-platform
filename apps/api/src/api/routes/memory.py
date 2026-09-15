"""API endpoints for Research Memory (Generation 3: Autonomous Research)."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from api.dependencies import (
    get_current_user,
    get_memory_manager,
    get_memory_repository,
    get_optional_current_user,
)
from database.models.memory import DBResearchMemory
from database.repositories.memory_repository import MemoryRepository
from research.memory.manager import ResearchMemoryManager
from research.memory.models import (
    MemoryItem,
    MemoryRecallResult,
    MemorySearchRequest,
    MemoryType,
)
from shared.auth import User
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


def _to_memory_item(item: DBResearchMemory) -> MemoryItem:
    """Helper to convert database record to API response model."""
    m_type = MemoryType(item.memory_type) if item.memory_type in [m.value for m in MemoryType] else MemoryType.FINDING
    return MemoryItem(
        id=str(item.id),
        user_id=str(item.user_id) if item.user_id else None,
        job_id=str(item.job_id) if item.job_id else None,
        project_id=item.project_id,
        memory_type=m_type,
        title=item.title,
        content=item.content,
        tags=item.tags or [],
        confidence=float(item.confidence_score or 1.0),
        confidence_score=float(item.confidence_score or 1.0),
        source_type=item.source_type if hasattr(item, "source_type") else "manual",
        created_at=item.created_at.isoformat() if item.created_at else None,
        last_accessed_at=item.last_accessed_at.isoformat() if item.last_accessed_at else None,
        access_count=item.access_count or 0,
        is_pinned=item.is_pinned or False,
        provenance=item.provenance_json or {},
        metadata=item.provenance_json or {},
    )


class CreateMemoryRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Concise memory title")
    content: str = Field(..., min_length=1, description="Detailed memory content")
    memory_type: MemoryType = Field(default=MemoryType.FINDING, description="Category of memory")
    job_id: Optional[str] = Field(default=None, description="Optional associated research job ID")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class UpdateMemoryRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    content: Optional[str] = Field(default=None, min_length=1)
    memory_type: Optional[MemoryType] = None
    tags: Optional[List[str]] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


@router.get("", response_model=List[MemoryItem])
async def list_memories(
    job_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_optional_current_user),
    memory_repo: MemoryRepository = Depends(get_memory_repository),
) -> List[MemoryItem]:
    """List cross-session research memories for current user."""
    user_uuid = UUID(str(current_user.id)) if current_user else None
    job_uuid = UUID(str(job_id)) if job_id else None
    tags_filter = [tag] if tag else None

    db_items = await memory_repo.list_memories(
        user_id=user_uuid,
        job_id=job_uuid,
        memory_type=memory_type,
        tags=tags_filter,
        limit=limit,
        offset=offset,
    )

    return [_to_memory_item(item) for item in db_items]


@router.post("", response_model=MemoryItem, status_code=status.HTTP_201_CREATED)
async def create_memory(
    req: CreateMemoryRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    memory_mgr: ResearchMemoryManager = Depends(get_memory_manager),
) -> MemoryItem:
    """Explicitly store a research insight, concept, or finding into memory."""
    user_id_str = str(current_user.id) if current_user else None
    return await memory_mgr.store_memory(
        title=req.title,
        content=req.content,
        memory_type=req.memory_type,
        user_id=user_id_str,
        job_id=req.job_id,
        tags=req.tags,
        confidence=req.confidence,
        source_type="user" if current_user else "manual",
        metadata=req.metadata,
    )


@router.get("/search", response_model=MemoryRecallResult)
async def recall_memories(
    query: str = Query(..., min_length=1, description="Semantic or text search query"),
    top_k: int = Query(5, ge=1, le=50, description="Max results"),
    memory_type: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    memory_mgr: ResearchMemoryManager = Depends(get_memory_manager),
) -> MemoryRecallResult:
    """Recall relevant conceptual memories across past research jobs."""
    user_id_str = str(current_user.id) if current_user else None
    tags_filter = [tag] if tag else None

    return await memory_mgr.recall_memories(
        user_id=user_id_str,
        query=query,
        top_k=top_k,
        memory_type=memory_type,
        tags=tags_filter,
    )


@router.get("/{memory_id}", response_model=MemoryItem)
async def get_memory(
    memory_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    memory_repo: MemoryRepository = Depends(get_memory_repository),
) -> MemoryItem:
    """Retrieve a single research memory item."""
    try:
        mem_uuid = UUID(memory_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID UUID")

    db_item = await memory_repo.get_by_id(mem_uuid)
    if not db_item:
        raise HTTPException(status_code=404, detail="Memory item not found")

    if current_user and db_item.user_id and str(db_item.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this memory")

    await memory_repo.increment_access(mem_uuid)
    return _to_memory_item(db_item)


@router.patch("/{memory_id}", response_model=MemoryItem)
async def update_memory(
    memory_id: str,
    req: UpdateMemoryRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    memory_repo: MemoryRepository = Depends(get_memory_repository),
) -> MemoryItem:
    """Update title, content, tags, or confidence of a memory item."""
    try:
        mem_uuid = UUID(memory_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID UUID")

    db_item = await memory_repo.get_by_id(mem_uuid)
    if not db_item:
        raise HTTPException(status_code=404, detail="Memory item not found")

    if current_user and db_item.user_id and str(db_item.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this memory")

    update_fields: Dict[str, Any] = {}
    if req.title is not None:
        update_fields["title"] = req.title
    if req.content is not None:
        update_fields["content"] = req.content
    if req.memory_type is not None:
        update_fields["memory_type"] = req.memory_type.value if hasattr(req.memory_type, "value") else str(req.memory_type)
    if req.tags is not None:
        update_fields["tags"] = req.tags
    if req.confidence is not None:
        update_fields["confidence_score"] = req.confidence
    if req.metadata is not None:
        update_fields["provenance"] = req.metadata

    updated = await memory_repo.update(mem_uuid, **update_fields)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update memory item")

    return _to_memory_item(updated)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    memory_repo: MemoryRepository = Depends(get_memory_repository),
) -> None:
    """Delete a memory item from persistent storage."""
    try:
        mem_uuid = UUID(memory_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID UUID")

    db_item = await memory_repo.get_by_id(mem_uuid)
    if not db_item:
        raise HTTPException(status_code=404, detail="Memory item not found")

    if current_user and db_item.user_id and str(db_item.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this memory")

    deleted = await memory_repo.delete(mem_uuid)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete memory item")
