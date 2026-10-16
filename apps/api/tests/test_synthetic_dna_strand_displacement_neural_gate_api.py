"""Tests for Phase 570: Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base, get_db_session
from main import app


@pytest_asyncio.fixture
async def async_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_synthetic_dna_strand_displacement_neural_gate_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine Integration Test",
        "target_specimen": "Toehold-Mediated 4-Input 2-Class DNA Strand Displacement Reaction Network in Tris-Acetate-EDTA Buffer",
        "analytical_modality": "dsd-molecular-neural-classification",
        "input_scale": 1.0,
    }
    response = await async_client.post("/api/v1/synthetic-dna-strand-displacement-neural-gate/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine Integration Test"
    assert data["toehold_exchange_rate_constant_m_s"] != 0.0
    assert data["confidence_score"] >= 0.90
    assert len(data["item_profiles"]) == 3
    assert len(data["metric_traces"]) == 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/synthetic-dna-strand-displacement-neural-gate/studies/{study_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == study_id

    list_resp = await async_client.get("/api/v1/synthetic-dna-strand-displacement-neural-gate/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
