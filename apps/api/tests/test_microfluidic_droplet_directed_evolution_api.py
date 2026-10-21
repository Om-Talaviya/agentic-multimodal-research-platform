"""Tests for Phase 577: Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator API."""

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
async def test_microfluidic_droplet_directed_evolution_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator Integration Test",
        "target_specimen": "Picoliter Water-in-Oil Droplet Encapsulated TEM-1 β-Lactamase Saturation Mutagenesis Library",
        "analytical_modality": "microfluidic-droplet-directed-evolution",
        "input_scale": 1.0,
    }
    response = await async_client.post("/api/v1/microfluidic-droplet-directed-evolution/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator Integration Test"
    assert data["droplet_generation_rate_hz"] != 0.0
    assert data["confidence_score"] >= 0.90
    assert len(data["item_profiles"]) == 3
    assert len(data["metric_traces"]) == 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/microfluidic-droplet-directed-evolution/studies/{study_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == study_id

    list_resp = await async_client.get("/api/v1/microfluidic-droplet-directed-evolution/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1


@pytest.mark.asyncio
async def test_microfluidic_droplet_directed_evolution_api_nonexistent_study(async_client: AsyncClient):
    random_uuid = "00000000-0000-0000-0000-000000000000"
    get_resp = await async_client.get(f"/api/v1/microfluidic-droplet-directed-evolution/studies/{random_uuid}")
    assert get_resp.status_code == 404
    err_data = get_resp.json()
    assert "not found" in err_data.get("detail", "").lower()


@pytest.mark.asyncio
async def test_microfluidic_droplet_directed_evolution_api_validation_bounds(async_client: AsyncClient):
    # Test below minimum bound (ge=0.1)
    payload_low = {
        "name": "Validation Test Low",
        "input_scale": 0.05,
    }
    resp_low = await async_client.post("/api/v1/microfluidic-droplet-directed-evolution/analyze", json=payload_low)
    assert resp_low.status_code == 422

    # Test above maximum bound (le=10.0)
    payload_high = {
        "name": "Validation Test High",
        "input_scale": 15.0,
    }
    resp_high = await async_client.post("/api/v1/microfluidic-droplet-directed-evolution/analyze", json=payload_high)
    assert resp_high.status_code == 422

