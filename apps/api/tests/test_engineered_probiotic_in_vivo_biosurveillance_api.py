"""Tests for Phase 574: Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine API."""

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
async def test_engineered_probiotic_in_vivo_biosurveillance_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine Integration Test",
        "target_specimen": "Engineered Escherichia coli Nissle 1917 Dual-Input Nitric Oxide and Tetrathionate Responsive Memory Circuit",
        "analytical_modality": "probiotic-in-vivo-biosurveillance",
        "input_scale": 1.0,
    }
    response = await async_client.post("/api/v1/engineered-probiotic-in-vivo-biosurveillance/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine Integration Test"
    assert data["calprotectin_induction_fold_change"] != 0.0
    assert data["confidence_score"] >= 0.90
    assert len(data["item_profiles"]) == 3
    assert len(data["metric_traces"]) == 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/engineered-probiotic-in-vivo-biosurveillance/studies/{study_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == study_id

    list_resp = await async_client.get("/api/v1/engineered-probiotic-in-vivo-biosurveillance/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
