"""Tests for Phase 467: Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator API."""

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
async def test_tissue_origami_cell_sheet_folding_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator API Test",
        "target_specimen": "Bilayer C2C12 Myoblast / NIH-3T3 Fibroblast Sheet on Thermoresponsive PNIPAM Hydrogel",
        "analytical_modality": "4d-tissue-origami-folding",
        "input_scale": 1.0,
    }

    response = await async_client.post("/api/v1/tissue-origami-cell-sheet-folding/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator API Test"
    assert data["mean_curvature_folding_radius_mm"] != 0.0
    assert "item_profiles" in data
    assert "metric_traces" in data
    assert len(data["item_profiles"]) >= 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/tissue-origami-cell-sheet-folding/studies/{study_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == study_id

    list_resp = await async_client.get("/api/v1/tissue-origami-cell-sheet-folding/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
