"""Tests for UsageRepository and UserQuotaRepository."""

import pytest
import pytest_asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.usage_repo import UsageRepository
from database.repositories.quota_repo import UserQuotaRepository
from shared.exceptions import QuotaExceededError


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_usage_record_persistence_and_aggregation(async_db: AsyncSession):
    user_repo = UserRepository(async_db)
    usage_repo = UsageRepository(async_db)

    user = DBUser(username="test_telemetry", email="telemetry@example.com", password_hash="hash")
    await user_repo.create(user)
    await async_db.commit()

    # Record first usage
    rec1 = await usage_repo.record_usage(
        provider="ollama",
        model="llama3:8b",
        user_id=user.id,
        prompt_tokens=100,
        completion_tokens=50,
        cost_usd=0.0,
        latency_ms=120,
        success=True,
    )
    await async_db.commit()

    assert rec1.id is not None
    assert rec1.total_tokens == 150
    assert rec1.user_id == user.id

    # Record second usage (paid)
    rec2 = await usage_repo.record_usage(
        provider="gemini",
        model="gemini-2.5-pro",
        user_id=user.id,
        prompt_tokens=200,
        completion_tokens=100,
        cost_usd=0.0015,
        latency_ms=450,
        success=True,
    )
    await async_db.commit()

    # Record failed usage (should not contribute to daily totals if success=False)
    await usage_repo.record_usage(
        provider="openai",
        model="gpt-4o",
        user_id=user.id,
        prompt_tokens=50,
        completion_tokens=0,
        cost_usd=0.0005,
        latency_ms=10,
        success=False,
        error_message="Rate limited",
    )
    await async_db.commit()

    # Query usage records
    records = await usage_repo.get_user_usage(user.id)
    assert len(records) == 3

    # Check aggregations
    tokens_today = await usage_repo.get_total_tokens_today(user.id)
    cost_today = await usage_repo.get_total_cost_today(user.id)

    assert tokens_today == 150 + 300  # only successful records: 150 + 300 = 450
    assert abs(cost_today - 0.0015) < 1e-6


@pytest.mark.asyncio
async def test_user_quota_lifecycle_and_unlimited_defaults(async_db: AsyncSession):
    user_repo = UserRepository(async_db)
    quota_repo = UserQuotaRepository(async_db)

    user = DBUser(username="quota_user", email="quota@example.com", password_hash="hash")
    await user_repo.create(user)
    await async_db.commit()

    # Default quota creation — NULL limits signify unlimited
    quota = await quota_repo.get_or_create(user.id)
    await async_db.commit()

    assert quota.user_id == user.id
    assert quota.daily_token_limit is None  # NULL = unlimited
    assert quota.daily_cost_limit is None   # NULL = unlimited
    assert quota.tokens_used_today == 0
    assert quota.cost_used_today == 0.0

    # check_quota with NULL limit always returns True
    can_run = await quota_repo.check_quota(user.id, estimated_tokens=1000000, estimated_cost=100.0)
    assert can_run is True

    # Consuming quota without finite limit succeeds
    updated_quota = await quota_repo.reserve_or_consume_quota(user.id, tokens=5000, cost=0.05)
    await async_db.commit()

    assert updated_quota.tokens_used_today == 5000
    assert abs(updated_quota.cost_used_today - 0.05) < 1e-6


@pytest.mark.asyncio
async def test_user_quota_finite_limits_and_exceeded_error(async_db: AsyncSession):
    user_repo = UserRepository(async_db)
    quota_repo = UserQuotaRepository(async_db)

    user = DBUser(username="limited_user", email="limited@example.com", password_hash="hash")
    await user_repo.create(user)
    await async_db.commit()

    # Set finite quota limits
    await quota_repo.set_quota_limits(
        user_id=user.id,
        daily_token_limit=1000,
        daily_cost_limit=0.01,
    )
    await async_db.commit()

    # Check quota passes within limit
    assert await quota_repo.check_quota(user.id, estimated_tokens=800, estimated_cost=0.005) is True

    # Check quota fails when exceeding limit
    assert await quota_repo.check_quota(user.id, estimated_tokens=1200, estimated_cost=0.005) is False
    assert await quota_repo.check_quota(user.id, estimated_tokens=500, estimated_cost=0.02) is False

    # Consume within limit
    await quota_repo.reserve_or_consume_quota(user.id, tokens=800, cost=0.005)
    await async_db.commit()

    # Next consumption exceeding token limit raises QuotaExceededError
    with pytest.raises(QuotaExceededError) as exc_info:
        await quota_repo.reserve_or_consume_quota(user.id, tokens=300, cost=0.001)
    assert "Daily token quota exceeded" in str(exc_info.value)

    # Next consumption exceeding cost limit raises QuotaExceededError
    with pytest.raises(QuotaExceededError) as exc_cost:
        await quota_repo.reserve_or_consume_quota(user.id, tokens=50, cost=0.01)
    assert "Daily cost quota exceeded" in str(exc_cost.value)


@pytest.mark.asyncio
async def test_user_quota_daily_calendar_reset(async_db: AsyncSession):
    user_repo = UserRepository(async_db)
    quota_repo = UserQuotaRepository(async_db)

    user = DBUser(username="reset_user", email="reset@example.com", password_hash="hash")
    await user_repo.create(user)
    await async_db.commit()

    # Set finite limit and consume it
    quota = await quota_repo.set_quota_limits(user.id, daily_token_limit=500, daily_cost_limit=0.01)
    await quota_repo.reserve_or_consume_quota(user.id, tokens=500, cost=0.01)
    await async_db.commit()

    assert quota.tokens_used_today == 500

    # Simulate yesterday's reset date
    quota.last_reset_at = datetime.now(UTC) - timedelta(days=1, hours=1)
    await async_db.commit()

    # When checked or consumed on the new day, counters automatically reset
    reset_occurred = quota_repo._check_and_reset_if_needed(quota)
    assert reset_occurred is True
    assert quota.tokens_used_today == 0
    assert quota.cost_used_today == 0.0

    # Now operations are allowed again on the new day
    assert await quota_repo.check_quota(user.id, estimated_tokens=400) is True
