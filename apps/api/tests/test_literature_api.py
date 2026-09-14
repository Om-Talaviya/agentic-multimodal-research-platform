"""Integration tests for Systematic Literature Review & Meta-Analysis REST API endpoints."""

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
        username="slr_api_user",
        email="slr_api@test.com",
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
async def test_literature_api_workflow(api_client: AsyncClient):
    """Test full SLR creation, criteria, candidate addition, screening, and meta-analysis via REST API."""
    # 1. Create Literature Review
    create_resp = await api_client.post(
        "/api/v1/literature/reviews",
        json={
            "title": "Quantum Error Mitigation in Noisy Intermediate-Scale Quantum (NISQ) Processors",
            "research_question": "What is the relative error reduction of zero-noise extrapolation vs probabilistic error cancellation?",
            "protocol_type": "PRISMA-2020",
            "pico_framework": {
                "population": "Superconducting Qubits",
                "intervention": "Zero-Noise Extrapolation",
                "comparator": "Unmitigated Baseline",
                "outcome": "Quantum State Fidelity",
            },
        },
    )
    assert create_resp.status_code == 201
    review_data = create_resp.json()
    review_id = review_data["id"]
    assert review_data["title"] == "Quantum Error Mitigation in Noisy Intermediate-Scale Quantum (NISQ) Processors"

    # 2. Add Inclusion Criterion
    crit_resp = await api_client.post(
        f"/api/v1/literature/reviews/{review_id}/criteria",
        json={
            "criterion_type": "inclusion",
            "description": "Experimental validation on >5 physical qubits",
            "category": "hardware_scale",
        },
    )
    assert crit_resp.status_code == 201

    # 3. Add Candidate Studies
    add_studies_resp = await api_client.post(
        f"/api/v1/literature/reviews/{review_id}/candidates",
        json={
            "studies": [
                {
                    "title": "ZNE on 16-Qubit Rigetti Processor (2025)",
                    "authors": ["Alice et al."],
                    "publication_year": 2025,
                    "sample_size": 1000,
                    "effect_size": 0.75,
                    "variance": 0.03,
                },
                {
                    "title": "PEC on IBM Quantum Falcon (2024)",
                    "authors": ["Bob et al."],
                    "publication_year": 2024,
                    "sample_size": 800,
                    "effect_size": 0.68,
                    "variance": 0.035,
                },
            ],
        },
    )
    assert add_studies_resp.status_code == 201
    assert add_studies_resp.json()["added_count"] == 2

    # 4. Fetch Review to get Candidate IDs
    get_review_resp = await api_client.get(f"/api/v1/literature/reviews/{review_id}")
    assert get_review_resp.status_code == 200
    review_detail = get_review_resp.json()
    assert len(review_detail["candidates"]) == 2

    cand_1_id = review_detail["candidates"][0]["id"]
    cand_2_id = review_detail["candidates"][1]["id"]

    # 5. Screen candidates to 'included'
    screen_resp1 = await api_client.patch(
        f"/api/v1/literature/reviews/{review_id}/candidates/{cand_1_id}",
        json={"screening_status": "included"},
    )
    assert screen_resp1.status_code == 200

    screen_resp2 = await api_client.patch(
        f"/api/v1/literature/reviews/{review_id}/candidates/{cand_2_id}",
        json={"screening_status": "included"},
    )
    assert screen_resp2.status_code == 200

    # 6. Run Meta-Analysis
    meta_resp = await api_client.post(
        f"/api/v1/literature/reviews/{review_id}/meta-analysis",
        json={
            "synthesis_name": "NISQ Fidelity Enhancement",
            "effect_metric": "hedges_g",
            "model_type": "random_effects",
        },
    )
    assert meta_resp.status_code == 201
    meta_data = meta_resp.json()
    assert meta_data["total_studies_analyzed"] == 2
    assert meta_data["pooled_effect_size"] > 0
    assert len(meta_data["forest_plot_data"]) == 2

    # 7. Check PRISMA Flow
    flow_resp = await api_client.get(f"/api/v1/literature/reviews/{review_id}/prisma-flow")
    assert flow_resp.status_code == 200
    flow_data = flow_resp.json()
    assert flow_data["identification"]["records_identified_databases"] == 2
    assert flow_data["included"]["studies_included_in_review"] == 2

    # 8. Check Platform Metrics
    metrics_resp = await api_client.get("/api/v1/literature/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["total_reviews"] >= 1
    assert metrics_data["total_meta_analyses"] >= 1
