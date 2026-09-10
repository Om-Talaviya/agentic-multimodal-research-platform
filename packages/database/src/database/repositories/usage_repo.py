"""Usage record repository."""

from datetime import UTC, datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.usage_record import UsageRecord


def utc_now() -> datetime:
    return datetime.now(UTC)


class UsageRepository:
    """Repository for managing AI model usage records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_usage(
        self,
        provider: str,
        model: str,
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        request_type: str = "complete",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: Optional[int] = None,
        cost_usd: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None,
        latency_ms: Optional[int] = None,
    ) -> UsageRecord:
        """Create and persist a new model usage record."""
        total = total_tokens if total_tokens is not None else (prompt_tokens + completion_tokens)
        record = UsageRecord(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            provider=provider,
            model=model,
            request_type=request_type,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            cost_usd=cost_usd,
            success=success,
            error_message=error_message,
            latency_ms=latency_ms,
            created_at=utc_now(),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_user_usage(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[UsageRecord]:
        """List usage records for a specific user ordered by created_at desc."""
        query = (
            select(UsageRecord)
            .where(UsageRecord.user_id == user_id)
            .order_by(UsageRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_tokens_today(self, user_id: UUID) -> int:
        """Calculate total tokens consumed by user today in UTC."""
        today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            select(func.coalesce(func.sum(UsageRecord.total_tokens), 0))
            .where(
                UsageRecord.user_id == user_id,
                UsageRecord.created_at >= today_start,
                UsageRecord.success == True,  # noqa: E712
            )
        )
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def get_total_cost_today(self, user_id: UUID) -> float:
        """Calculate total USD cost incurred by user today in UTC."""
        today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            select(func.coalesce(func.sum(UsageRecord.cost_usd), 0.0))
            .where(
                UsageRecord.user_id == user_id,
                UsageRecord.created_at >= today_start,
                UsageRecord.success == True,  # noqa: E712
            )
        )
        result = await self.session.execute(query)
        return float(result.scalar_one())
