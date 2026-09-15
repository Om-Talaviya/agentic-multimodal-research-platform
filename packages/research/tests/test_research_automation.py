"""Tests for ResearchAutomationEngine and cron computations."""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.connection import Base
from database.models.user import User
from database.repositories.automation_repo import AutomationRepository
from research.automation.engine import ResearchAutomationEngine, compute_next_run


@pytest.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()


def test_compute_next_run():
    base_time = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Hourly
    next_hourly = compute_next_run("@hourly", base_time)
    assert next_hourly == base_time + timedelta(hours=1)

    # Daily
    next_daily = compute_next_run("@daily", base_time)
    assert next_daily == base_time + timedelta(days=1)

    # Weekly
    next_weekly = compute_next_run("@weekly", base_time)
    assert next_weekly == base_time + timedelta(weeks=1)

    # Interval: every_6h
    next_6h = compute_next_run("every_6h", base_time)
    assert next_6h == base_time + timedelta(hours=6)

    # Cron step: */30 * * * *
    next_30m = compute_next_run("*/30 * * * *", base_time)
    assert next_30m == base_time + timedelta(minutes=30)


def test_detect_novelty():
    repo = None  # Not needed for pure method
    engine = ResearchAutomationEngine(repo=repo)  # type: ignore

    previous_claims = [
        "LLMs exhibit emergent reasoning at large parameter counts",
        "Transformer attention is quadratic in sequence length",
    ]

    # Exact overlap test
    same_claims = [
        {"claim": "LLMs exhibit emergent reasoning at large parameter counts"},
        {"claim": "Transformer attention is quadratic in sequence length"},
    ]
    score, novel = engine.detect_novelty(previous_claims, same_claims)
    assert score == 0.0
    assert len(novel) == 0

    # Novel claims test
    mixed_claims = [
        {"claim": "LLMs exhibit emergent reasoning at large parameter counts"},
        {"claim": "Linear attention achieves state-of-the-art memory efficiency on 1M context"},
    ]
    score, novel = engine.detect_novelty(previous_claims, mixed_claims)
    assert score == 0.5
    assert len(novel) == 1
    assert "Linear attention" in novel[0]["claim"]


@pytest.mark.asyncio
async def test_execute_sweep_run_and_alerts(test_session: AsyncSession):
    user = User(
        id=uuid.uuid4(),
        username="sweep_tester",
        email="sweeper@automation.ai",
        password_hash="hash",
        role="Researcher",
    )
    test_session.add(user)
    await test_session.commit()

    repo = AutomationRepository(test_session)
    engine = ResearchAutomationEngine(repo=repo)

    # Create schedule with 20% novelty threshold
    schedule = await repo.create_schedule(
        user_id=user.id,
        title="Superconductor Daily Monitor",
        query_topic="Room temperature superconductor LK-99 replications",
        novelty_threshold=0.20,
        webhook_url="https://webhook.site/dispatch",
    )

    # Execute first sweep (100% novel on blank slate)
    sweep_1 = await engine.execute_sweep_run(
        schedule_id=schedule.id,
        generated_findings=[
            {"claim": "Replication study A reports zero resistance at 110K", "confidence": 0.95}
        ],
    )

    assert sweep_1.novelty_score == 1.0
    assert sweep_1.alert_dispatched is True
    assert sweep_1.status == "alert_dispatched"

    # Verify alerts created
    alerts = await repo.list_alerts(schedule_id=schedule.id)
    assert len(alerts) >= 1

    # Execute second sweep with identical finding
    sweep_2 = await engine.execute_sweep_run(
        schedule_id=schedule.id,
        generated_findings=[
            {"claim": "Replication study A reports zero resistance at 110K", "confidence": 0.95}
        ],
    )
    assert sweep_2.novelty_score == 0.0
    assert sweep_2.alert_dispatched is False
    assert sweep_2.status == "no_novel_findings"
