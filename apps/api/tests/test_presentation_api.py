"""Integration tests for Presentations and Podcast REST API endpoints."""

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
        username="deck_api_user",
        email="deck@test.com",
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
async def test_presentation_and_podcast_api_lifecycle(api_client: AsyncClient):
    """Test generating presentation deck, fetching slides, generating podcast briefing, and querying metrics."""
    # 1. Generate Presentation Deck
    pres_resp = await api_client.post(
        "/api/v1/presentations",
        json={
            "title": "Quantum Error Mitigation Breakthroughs",
            "research_content": "Extensive empirical analysis demonstrated 34% fidelity enhancement across multi-qubit processors.",
            "target_audience": "executive",
            "theme": "midnight_slate",
        },
    )
    assert pres_resp.status_code == 201
    pres_data = pres_resp.json()
    pres_id = pres_data["id"]
    assert pres_data["title"] == "Quantum Error Mitigation Breakthroughs"
    assert pres_data["total_slides"] == 5
    assert len(pres_data["slides"]) == 5

    # 2. Get Presentation Details
    get_pres_resp = await api_client.get(f"/api/v1/presentations/{pres_id}")
    assert get_pres_resp.status_code == 200
    assert len(get_pres_resp.json()["slides"]) == 5

    # 3. Generate Podcast Briefing
    pod_resp = await api_client.post(
        "/api/v1/presentations/podcasts",
        json={
            "topic": "Quantum Error Mitigation",
            "key_findings": "Fidelity increased by 34% with zero-noise extrapolation.",
            "host_name": "Dr. Elena Vance (Host)",
            "expert_name": "Prof. Marcus Sterling (Specialist)",
        },
    )
    assert pod_resp.status_code == 201
    pod_data = pod_resp.json()
    pod_id = pod_data["id"]
    assert pod_data["total_dialogue_turns"] >= 5
    assert pod_data["status"] == "synthesized"

    # 4. Get Podcast Details
    get_pod_resp = await api_client.get(f"/api/v1/presentations/podcasts/{pod_id}")
    assert get_pod_resp.status_code == 200
    assert len(get_pod_resp.json()["dialogue_transcript_json"]) >= 5

    # 5. Check Platform Metrics
    metrics_resp = await api_client.get("/api/v1/presentations/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["total_presentations"] >= 1
    assert metrics_data["total_podcasts"] >= 1
