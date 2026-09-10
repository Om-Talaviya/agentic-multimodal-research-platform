"""User quota repository with row-locking concurrency control."""

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user_quota import UserQuota
from shared.exceptions import QuotaExceededError


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserQuotaRepository:
    """Repository for managing user quotas with transactional row-locking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, user_id: UUID) -> UserQuota:
        """Get or create quota record for user."""
        query = select(UserQuota).where(UserQuota.user_id == user_id)
        result = await self.session.execute(query)
        quota = result.scalar_one_or_none()

        if quota is None:
            quota = UserQuota(
                id=uuid4(),
                user_id=user_id,
                daily_token_limit=None,  # NULL = unlimited
                daily_cost_limit=None,   # NULL = unlimited
                tokens_used_today=0,
                cost_used_today=0.0,
                max_concurrent_jobs=None,
                last_reset_at=utc_now(),
                updated_at=utc_now(),
            )
            self.session.add(quota)
            await self.session.flush()

        return quota

    async def get_by_user_id(
        self,
        user_id: UUID,
        with_for_update: bool = False,
    ) -> Optional[UserQuota]:
        """Fetch quota with optional row-level lock (FOR UPDATE)."""
        query = select(UserQuota).where(UserQuota.user_id == user_id)
        if with_for_update:
            try:
                query = query.with_for_update()
            except Exception:
                pass
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _check_and_reset_if_needed(self, quota: UserQuota) -> bool:
        """Reset daily counters if a new UTC calendar day has started."""
        now = utc_now()
        last_reset = quota.last_reset_at
        if hasattr(last_reset, "astimezone"):
            last_reset_date = last_reset.astimezone(UTC).date()
        else:
            last_reset_date = last_reset.date()

        today_date = now.date()
        if last_reset_date < today_date:
            quota.tokens_used_today = 0
            quota.cost_used_today = 0.0
            quota.last_reset_at = now
            quota.updated_at = now
            return True
        return False

    async def check_quota(
        self,
        user_id: UUID,
        estimated_tokens: int = 0,
        estimated_cost: float = 0.0,
    ) -> bool:
        """Check if user has sufficient quota for an estimated operation without consuming it."""
        quota = await self.get_by_user_id(user_id, with_for_update=False)
        if quota is None:
            quota = await self.get_or_create(user_id)
        self._check_and_reset_if_needed(quota)

        if quota.daily_token_limit is not None:
            if quota.tokens_used_today + estimated_tokens > quota.daily_token_limit:
                return False

        if quota.daily_cost_limit is not None:
            if quota.cost_used_today + estimated_cost > quota.daily_cost_limit:
                return False

        return True

    async def reserve_or_consume_quota(
        self,
        user_id: UUID,
        tokens: int = 0,
        cost: float = 0.0,
        with_for_update: bool = True,
    ) -> UserQuota:
        """Atomically check and consume quota within an active transaction.
        
        Raises QuotaExceededError if the requested tokens/cost would exceed configured finite limits.
        """
        quota = await self.get_by_user_id(user_id, with_for_update=with_for_update)
        if quota is None:
            quota = await self.get_or_create(user_id)

        self._check_and_reset_if_needed(quota)

        # Token limit check (NULL = unlimited)
        if quota.daily_token_limit is not None:
            if quota.tokens_used_today + tokens > quota.daily_token_limit:
                raise QuotaExceededError(
                    f"Daily token quota exceeded. Limit: {quota.daily_token_limit}, "
                    f"Used: {quota.tokens_used_today}, Requested: {tokens}",
                    details={
                        "user_id": str(user_id),
                        "daily_token_limit": quota.daily_token_limit,
                        "tokens_used_today": quota.tokens_used_today,
                        "requested_tokens": tokens,
                    },
                )

        # Cost limit check (NULL = unlimited)
        if quota.daily_cost_limit is not None:
            if quota.cost_used_today + cost > quota.daily_cost_limit:
                raise QuotaExceededError(
                    f"Daily cost quota exceeded. Limit: ${quota.daily_cost_limit:.4f}, "
                    f"Used: ${quota.cost_used_today:.4f}, Requested: ${cost:.4f}",
                    details={
                        "user_id": str(user_id),
                        "daily_cost_limit": quota.daily_cost_limit,
                        "cost_used_today": quota.cost_used_today,
                        "requested_cost": cost,
                    },
                )

        quota.tokens_used_today += tokens
        quota.cost_used_today += cost
        quota.updated_at = utc_now()
        await self.session.flush()
        return quota

    async def set_quota_limits(
        self,
        user_id: UUID,
        daily_token_limit: Optional[int] = None,
        daily_cost_limit: Optional[float] = None,
        max_concurrent_jobs: Optional[int] = None,
    ) -> UserQuota:
        """Set or update quota limits for a user."""
        quota = await self.get_or_create(user_id)
        quota.daily_token_limit = daily_token_limit
        quota.daily_cost_limit = daily_cost_limit
        if max_concurrent_jobs is not None:
            quota.max_concurrent_jobs = max_concurrent_jobs
        quota.updated_at = utc_now()
        await self.session.flush()
        return quota
