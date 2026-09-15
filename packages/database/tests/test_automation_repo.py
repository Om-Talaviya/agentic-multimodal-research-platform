"""Tests for AutomationRepository."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.connection import Base
from database.models.user import User
from database.repositories.automation_repo import AutomationRepository


@pytest.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_manage_schedules(test_session: AsyncSession):
    # Setup test user
    user = User(
        id=uuid.uuid4(),
        username="automation_tester",
        email="tester@automation.ai",
        password_hash="hash",
        role="Researcher",
    )
    test_session.add(user)
    await test_session.commit()

    repo = AutomationRepository(test_session)

    # 1. Create schedule
    schedule = await repo.create_schedule(
        user_id=user.id,
        title="Solid-State Battery Monitoring",
        query_topic="What are the latest solid-state electrolyte breakthroughs?",
        cron_expression="@daily",
        routing_profile="quality_maximized",
        novelty_threshold=0.25,
        webhook_url="https://webhook.site/test-alert",
    )

    assert schedule is not None
    assert schedule.title == "Solid-State Battery Monitoring"
    assert schedule.status == "active"
    assert schedule.novelty_threshold == 0.25
    assert schedule.total_sweeps_count == 0

    # 2. Get schedule
    fetched = await repo.get_schedule(schedule.id)
    assert fetched is not None
    assert fetched.id == schedule.id

    # 3. List schedules
    schedules = await repo.list_schedules(user_id=user.id)
    assert len(schedules) == 1

    # 4. Pause and Resume
    paused = await repo.pause_schedule(schedule.id)
    assert paused.status == "paused"

    resumed = await repo.resume_schedule(schedule.id)
    assert resumed.status == "active"

    # 5. Record sweep result
    sweep = await repo.record_sweep_result(
        schedule_id=schedule.id,
        status="completed",
        findings_count=4,
        novel_claims_count=2,
        novelty_score=0.5,
        novel_claims=[{"claim": "Novel polymer composite electrolyte", "confidence": 0.94}],
        alert_dispatched=True,
        execution_duration_ms=1200.0,
        findings_summary="2 novel claims found",
    )
    assert sweep is not None
    assert sweep.novel_claims_count == 2
    assert sweep.alert_dispatched is True

    # Verify schedule totals updated
    updated_schedule = await repo.get_schedule(schedule.id)
    assert updated_schedule.total_sweeps_count == 1
    assert updated_schedule.last_findings_summary == "2 novel claims found"

    # 6. Create & Acknowledge Alert
    alert = await repo.create_alert(
        schedule_id=schedule.id,
        sweep_id=sweep.id,
        title="High Novelty Finding in Electrolytes",
        message="Novel polymer composite electrolyte discovered.",
        severity="warning",
        channel="in_app",
        payload={"novelty_score": 0.5},
    )
    assert alert is not None
    assert alert.is_acknowledged is False

    alerts = await repo.list_alerts(schedule_id=schedule.id)
    assert len(alerts) == 1

    acked = await repo.acknowledge_alert(alert.id)
    assert acked is not None
    assert acked.is_acknowledged is True
    assert acked.acknowledged_at is not None

    # 7. Metrics aggregation
    metrics = await repo.get_automation_metrics()
    assert metrics["total_schedules"] == 1
    assert metrics["active_schedules"] == 1
    assert metrics["total_sweeps"] == 1
    assert metrics["total_alerts"] == 1
    assert metrics["unacknowledged_alerts"] == 0

    # 8. Delete schedule
    deleted = await repo.delete_schedule(schedule.id)
    assert deleted is True
    assert await repo.get_schedule(schedule.id) is None
