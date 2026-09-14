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
        username="peer_review_user",
        email="peer@test.com",
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
async def test_peer_review_api_full_workflow(api_client: AsyncClient):

    """Test manuscript submission, multi-agent review, revisions, publication, and metrics."""
    # 1. Submit Manuscript
    submit_resp = await api_client.post(
        "/api/v1/publishing/manuscripts",
        json={
            "title": "Autonomous Consensus in Multi-Agent Debate Systems",
            "abstract": "We evaluate truth-convergence properties across adversarial agent teams using formal game-theoretic models.",
            "field_of_study": "computer_science",
            "venue_format": "nature",
            "claimed_contributions": ["Nash equilibrium convergence bounds", "Empirical truth-tracking metrics"],
            "keywords": ["Multi-Agent", "Consensus", "Game Theory"],
        },
    )
    assert submit_resp.status_code == 201
    manuscript_data = submit_resp.json()
    manuscript_id = manuscript_data["id"]
    assert manuscript_data["title"] == "Autonomous Consensus in Multi-Agent Debate Systems"
    assert manuscript_data["status"] == "submitted"

    # 2. Get Manuscript Details
    get_resp = await api_client.get(f"/api/v1/publishing/manuscripts/{manuscript_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["venue_format"] == "nature"

    # 3. List Manuscripts
    list_resp = await api_client.get("/api/v1/publishing/manuscripts")
    assert list_resp.status_code == 200
    assert any(m["id"] == manuscript_id for m in list_resp.json())

    # 4. Trigger Multi-Agent Peer Review Simulation
    review_resp = await api_client.post(f"/api/v1/publishing/manuscripts/{manuscript_id}/review")
    assert review_resp.status_code == 200
    rev_data = review_resp.json()
    assert rev_data["referee_reports_count"] == 3
    assert rev_data["overall_score"] >= 5.0
    assert len(rev_data["reports"]) == 3

    # 5. Submit Revision & Rebuttal
    revision_resp = await api_client.post(
        f"/api/v1/publishing/manuscripts/{manuscript_id}/revisions",
        json={
            "auto_generate_rebuttal": True,
            "diff_summary": "Included full Nash equilibrium formal derivation in Section 2.",
        },
    )
    assert revision_resp.status_code == 201
    rev_result = revision_resp.json()
    assert rev_result["revision_round"] == 1
    assert "Dear Editor and Referees" in rev_result["rebuttal_letter"]

    # 6. Publish Accepted Manuscript
    publish_resp = await api_client.post(
        f"/api/v1/publishing/manuscripts/{manuscript_id}/publish",
        json={
            "authors": ["Om Talaviya", "DeepMind Autonomous Research Systems"],
            "publication_year": 2026,
        },
    )
    assert publish_resp.status_code == 200
    pub_data = publish_resp.json()
    assert pub_data["status"] == "published"
    assert "10.1038/s41586-026" in pub_data["camera_ready_doi"]
    assert "@article{" in pub_data["bibtex_citation"]

    # 7. Check Platform Metrics
    metrics_resp = await api_client.get("/api/v1/publishing/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["total_manuscripts"] >= 1
    assert metrics_data["total_referee_reports"] >= 3

    # 8. Delete Manuscript
    del_resp = await api_client.delete(f"/api/v1/publishing/manuscripts/{manuscript_id}")
    assert del_resp.status_code == 200
