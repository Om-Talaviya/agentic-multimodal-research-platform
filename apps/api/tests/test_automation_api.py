"""
Tests for Research Automation API endpoints (Phase 26).
"""

from uuid import UUID
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_optional_current_user
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from main import app
from shared.auth import User, UserRole, hash_password


@pytest.fixture
async def test_db():
    from database import connection as db_conn

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    orig_engine = db_conn.engine
    orig_maker = db_conn.async_session_maker

    db_conn.engine = test_engine
    db_conn.async_session_maker = test_session_maker

    # Create test user
    async with test_session_maker() as session:
        user_repo = UserRepository(session)
        auto_user = DBUser(
            id=UUID("33333333-3333-3333-3333-333333333333"),
            username="automation_lead",
            email="lead@automation.ai",
            password_hash=hash_password("AutoPass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(auto_user)
        await session.commit()

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def auth_user():
    return User(
        id="33333333-3333-3333-3333-333333333333",
        username="automation_lead",
        email="lead@automation.ai",
        role=UserRole.RESEARCHER,
    )


@pytest.mark.asyncio
async def test_automation_api_lifecycle(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a scheduled research sweep
        create_res = await client.post(
            "/api/v1/automation/schedules",
            json={
                "title": "Quantum Error Correction Sweeper",
                "query_topic": "What are the latest surface code threshold results?",
                "cron_expression": "@daily",
                "routing_profile": "quality_maximized",
                "novelty_threshold": 0.25,
                "contradiction_alert": True,
                "webhook_url": "https://webhook.site/test-qec",
            },
        )
        assert create_res.status_code == 201
        sched_data = create_res.json()
        sched_id = sched_data["id"]
        assert sched_data["title"] == "Quantum Error Correction Sweeper"
        assert sched_data["status"] == "active"

        # 2. List schedules
        list_res = await client.get("/api/v1/automation/schedules")
        assert list_res.status_code == 200
        schedules = list_res.json()
        assert len(schedules) >= 1

        # 3. Get single schedule
        get_res = await client.get(f"/api/v1/automation/schedules/{sched_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == sched_id

        # 4. Trigger manual sweep
        trigger_res = await client.post(
            f"/api/v1/automation/schedules/{sched_id}/trigger",
            json={
                "simulated_findings": [
                    {"claim": "Cat qubit architecture lowers hardware overhead by 5x", "confidence": 0.96}
                ]
            },
        )
        assert trigger_res.status_code == 200
        sweep_data = trigger_res.json()
        assert sweep_data["novelty_score"] == 1.0
        assert sweep_data["alert_dispatched"] is True

        # 5. List sweeps for schedule
        sweeps_res = await client.get(f"/api/v1/automation/schedules/{sched_id}/sweeps")
        assert sweeps_res.status_code == 200
        sweeps = sweeps_res.json()
        assert len(sweeps) >= 1

        # 6. List alerts & acknowledge
        alerts_res = await client.get("/api/v1/automation/alerts")
        assert alerts_res.status_code == 200
        alerts = alerts_res.json()
        assert len(alerts) >= 1

        alert_id = alerts[0]["id"]
        ack_res = await client.patch(f"/api/v1/automation/alerts/{alert_id}/acknowledge")
        assert ack_res.status_code == 200
        assert ack_res.json()["is_acknowledged"] is True

        # 7. Get automation metrics
        metrics_res = await client.get("/api/v1/automation/metrics")
        assert metrics_res.status_code == 200
        metrics = metrics_res.json()
        assert metrics["total_schedules"] >= 1
        assert metrics["total_sweeps"] >= 1

        # 8. Pause and Resume
        pause_res = await client.patch(f"/api/v1/automation/schedules/{sched_id}/pause")
        assert pause_res.status_code == 200
        assert pause_res.json()["status"] == "paused"

        resume_res = await client.patch(f"/api/v1/automation/schedules/{sched_id}/resume")
        assert resume_res.status_code == 200
        assert resume_res.json()["status"] == "active"

        # 9. Delete schedule
        del_res = await client.delete(f"/api/v1/automation/schedules/{sched_id}")
        assert del_res.status_code == 200

    app.dependency_overrides.clear()
