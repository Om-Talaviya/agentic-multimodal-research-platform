"""Integration tests for Debate REST API endpoints."""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_current_user, get_db_session
from database.connection import Base
from database.models.user import User
from main import app


@pytest.fixture
async def api_client():
    """Create test client with in-memory SQLite and auth override."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    test_user = User(
        id=uuid.uuid4(),
        username="arbiter_user",
        email="arbiter@test.com",
        password_hash="hash",
        role="researcher",
    )

    async def override_get_db_session():
        async with async_session_factory() as session:
            yield session

    async def override_get_current_user():
        return test_user

    async with async_session_factory() as session:
        session.add(test_user)
        await session.commit()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_debate_api_workflow(api_client: AsyncClient):
    """Test creating, executing rounds, and fetching debate metrics via REST API."""
    # 1. Create Debate
    create_resp = await api_client.post(
        "/api/v1/debates",
        json={
            "topic": "Neuromorphic Computing vs Traditional GPUs",
            "initial_thesis": "Spiking neural networks offer 100x energy efficiency for edge inference.",
            "max_rounds": 2,
        },
    )
    assert create_resp.status_code == 201
    debate_data = create_resp.json()
    debate_id = debate_data["id"]
    assert debate_data["status"] == "active"
    assert debate_data["max_rounds"] == 2

    # 2. List Debates
    list_resp = await api_client.get("/api/v1/debates")
    assert list_resp.status_code == 200
    debates = list_resp.json()
    assert len(debates) >= 1

    # 3. Advance Round 1
    round_resp = await api_client.post(
        f"/api/v1/debates/{debate_id}/rounds",
        json={"run_to_completion": False},
    )
    assert round_resp.status_code == 200
    round_data = round_resp.json()
    assert round_data["round_number"] == 1

    # 4. Fetch Debate Details
    detail_resp = await api_client.get(f"/api/v1/debates/{debate_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["rounds"]) == 1

    # 5. Fetch Metrics
    metrics_resp = await api_client.get("/api/v1/debates/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    assert metrics["total_debates"] >= 1
