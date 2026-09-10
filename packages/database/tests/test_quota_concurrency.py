"""Tests for UserQuota concurrency and row-level locking."""

import asyncio
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.quota_repo import UserQuotaRepository
from shared.exceptions import QuotaExceededError


from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture
async def async_session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield session_maker
    await engine.dispose()


@pytest.mark.asyncio
async def test_quota_concurrency_finite_limit_not_oversubscribed(async_session_factory):
    """Test that concurrent requests attempting to consume quota past a finite limit do not oversubscribe it."""
    # 1. Setup user and quota in initial session
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        quota_repo = UserQuotaRepository(session)

        user = DBUser(username="concurrent_user", email="concurrent@example.com", password_hash="hash")
        await user_repo.create(user)
        await session.commit()

        # Set finite quota: 1000 tokens limit
        await quota_repo.set_quota_limits(user_id=user.id, daily_token_limit=1000)
        await session.commit()
        user_id = user.id

    # 2. Spawn 10 concurrent tasks each attempting to consume 200 tokens (Total = 2000 > 1000 limit)
    # Exactly 5 should succeed (5 * 200 = 1000), and 5 must fail with QuotaExceededError.
    successes = 0
    failures = 0

    async def worker():
        nonlocal successes, failures
        async with async_session_factory() as session:
            repo = UserQuotaRepository(session)
            try:
                await repo.reserve_or_consume_quota(user_id=user_id, tokens=200, cost=0.001, with_for_update=True)
                await session.commit()
                successes += 1
            except QuotaExceededError:
                await session.rollback()
                failures += 1

    for _ in range(10):
        await worker()

    assert successes == 5
    assert failures == 5

    # Verify final persisted quota state
    async with async_session_factory() as session:
        repo = UserQuotaRepository(session)
        final_quota = await repo.get_by_user_id(user_id)
        assert final_quota is not None
        assert final_quota.tokens_used_today == 1000
