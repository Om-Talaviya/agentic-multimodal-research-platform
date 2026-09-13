"""Repository for research memory operations (Phase 16)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.memory import DBResearchMemory


class MemoryRepository:
    """Repository for CRUD, search, and access tracking on research memories."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, memory: DBResearchMemory) -> DBResearchMemory:
        """Persist a new research memory."""
        self.session.add(memory)
        await self.session.flush()
        return memory

    async def batch_create(self, memories: List[DBResearchMemory]) -> List[DBResearchMemory]:
        """Persist multiple research memories in a single batch."""
        if not memories:
            return []
        self.session.add_all(memories)
        await self.session.flush()
        return memories

    async def get_by_id(self, memory_id: UUID) -> Optional[DBResearchMemory]:
        """Retrieve a specific memory item by ID."""
        result = await self.session.execute(
            select(DBResearchMemory).where(DBResearchMemory.id == memory_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: UUID,
        memory_type: Optional[str] = None,
        project_id: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBResearchMemory]:
        """List research memories for a specific user with optional filters."""
        return await self.list_memories(
            user_id=user_id,
            memory_type=memory_type,
            project_id=project_id,
            is_pinned=is_pinned,
            tags=[tag] if tag else None,
            limit=limit,
            offset=offset,
        )

    async def list_memories(
        self,
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        memory_type: Optional[str] = None,
        project_id: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBResearchMemory]:
        """List research memories with flexible filters."""
        stmt = select(DBResearchMemory)

        if user_id is not None:
            stmt = stmt.where(DBResearchMemory.user_id == user_id)
        if job_id is not None:
            stmt = stmt.where(DBResearchMemory.job_id == job_id)
        if memory_type:
            stmt = stmt.where(DBResearchMemory.memory_type == memory_type)
        if project_id:
            stmt = stmt.where(DBResearchMemory.project_id == project_id)
        if is_pinned is not None:
            stmt = stmt.where(DBResearchMemory.is_pinned == is_pinned)

        stmt = (
            stmt.order_by(
                DBResearchMemory.is_pinned.desc(),
                DBResearchMemory.updated_at.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        memories = list(result.scalars().all())

        if tags:
            clean_tags = [t.lower().strip() for t in tags if t]
            if clean_tags:
                memories = [
                    m for m in memories
                    if any(
                        any(ct in str(mt).lower() for mt in (m.tags or []))
                        for ct in clean_tags
                    )
                ]

        return memories

    async def search_by_text(
        self,
        arg1: Any = None,
        arg2: Any = None,
        query: Optional[str] = None,
        user_id: Optional[UUID] = None,
        memory_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[DBResearchMemory]:
        """Search memory items by title or content text match. Supports both (user_id, query) and (query, user_id)."""
        search_query = query
        target_user_id = user_id

        if isinstance(arg1, UUID):
            target_user_id = arg1
            if isinstance(arg2, str):
                search_query = arg2
        elif isinstance(arg1, str):
            search_query = arg1
            if isinstance(arg2, UUID):
                target_user_id = arg2

        if not search_query:
            search_query = ""

        search_terms = [t.strip() for t in search_query.split() if len(t.strip()) > 2]
        if not search_terms:
            search_terms = [search_query.strip()] if search_query.strip() else []

        conditions = []
        for term in search_terms:
            pattern = f"%{term}%"
            conditions.append(DBResearchMemory.title.ilike(pattern))
            conditions.append(DBResearchMemory.content.ilike(pattern))

        stmt = select(DBResearchMemory)
        if conditions:
            stmt = stmt.where(or_(*conditions))

        if target_user_id is not None:
            stmt = stmt.where(DBResearchMemory.user_id == target_user_id)
        if memory_type:
            stmt = stmt.where(DBResearchMemory.memory_type == memory_type)

        stmt = stmt.order_by(
            DBResearchMemory.is_pinned.desc(),
            DBResearchMemory.confidence_score.desc()
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        memory_id: UUID,
        user_id: Optional[UUID] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        memory_type: Optional[str] = None,
        confidence_score: Optional[float] = None,
        confidence: Optional[float] = None,
        tags: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
        provenance: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[DBResearchMemory]:
        """Update properties of an existing research memory."""
        memory = await self.get_by_id(memory_id)
        if not memory:
            return None
        if user_id is not None and memory.user_id != user_id:
            return None

        if title is not None:
            memory.title = title
        if content is not None:
            memory.content = content
        if memory_type is not None:
            memory.memory_type = memory_type
        if confidence_score is not None:
            memory.confidence_score = confidence_score
        elif confidence is not None:
            memory.confidence_score = confidence
        if tags is not None:
            memory.tags = tags
        if is_pinned is not None:
            memory.is_pinned = is_pinned
        if provenance is not None:
            memory.provenance_json = provenance
        elif metadata is not None:
            memory.provenance_json = metadata

        memory.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return memory

    async def increment_access(self, memory_id: UUID) -> None:
        """Increment access count and update last_accessed_at timestamp."""
        now = datetime.now(timezone.utc)
        await self.session.execute(
            update(DBResearchMemory)
            .where(DBResearchMemory.id == memory_id)
            .values(
                access_count=DBResearchMemory.access_count + 1,
                last_accessed_at=now,
            )
        )
        await self.session.flush()

    async def delete(self, memory_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """Delete a research memory item."""
        memory = await self.get_by_id(memory_id)
        if not memory:
            return False
        if user_id is not None and memory.user_id != user_id:
            return False

        await self.session.delete(memory)
        await self.session.flush()
        return True

    async def count_for_user(self, user_id: UUID) -> int:
        """Count total memory items for a user."""
        result = await self.session.execute(
            select(func.count(DBResearchMemory.id)).where(DBResearchMemory.user_id == user_id)
        )
        return result.scalar() or 0
