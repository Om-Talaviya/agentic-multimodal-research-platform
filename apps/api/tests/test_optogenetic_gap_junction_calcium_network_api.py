"""Tests for Phase 554: Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster API."""

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

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_optogenetic_gap_junction_calcium_network_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster API Test",
        "target_specimen": "Confluent Monolayer of Human Induced Pluripotent Stem Cell-Derived Cardiomyocytes expressing Channelrhodopsin-2 and Connexin-43",
        "analytical_modality": "optogenetic-gap-junction-sync",
        "input_scale": 1.0,
    }

    response = await async_client.post("/api/v1/optogenetic-gap-junction-calcium-network/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster API Test"
    assert data["calcium_wave_propagation_velocity_um_s"] != 0.0
    assert "item_profiles" in data
    assert "metric_traces" in data
    assert len(data["item_profiles"]) >= 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/optogenetic-gap-junction-calcium-network/studies/{study_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == study_id

    list_resp = await async_client.get("/api/v1/optogenetic-gap-junction-calcium-network/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
