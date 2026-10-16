"""Tests for Phase 571: Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler API."""

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
async def test_single_cell_spatial_epigenomic_cut_and_tag_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler Integration Test",
        "target_specimen": "Murine Embryonic Cortex Cryosection Microfluidic Deterministic Barcoding CUT&Tag for H3K27me3 and H3K4me3",
        "analytical_modality": "spatial-cut-and-tag-epigenomics",
        "input_scale": 1.0,
    }
    response = await async_client.post("/api/v1/single-cell-spatial-epigenomic-cut-and-tag/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler Integration Test"
    assert data["chromatin_enrichment_specificity"] != 0.0
    assert data["confidence_score"] >= 0.90
    assert len(data["item_profiles"]) == 3
    assert len(data["metric_traces"]) == 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/single-cell-spatial-epigenomic-cut-and-tag/studies/{study_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == study_id

    list_resp = await async_client.get("/api/v1/single-cell-spatial-epigenomic-cut-and-tag/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
