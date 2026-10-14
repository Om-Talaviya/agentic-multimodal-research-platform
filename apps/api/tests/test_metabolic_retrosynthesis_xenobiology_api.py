"""Tests for Phase 507: Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator API."""

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
async def test_metabolic_retrosynthesis_xenobiology_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator API Test",
        "target_specimen": "In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes",
        "analytical_modality": "xenobiotic-retrosynthesis-flux",
        "input_scale": 1.0,
    }

    response = await async_client.post("/api/v1/metabolic-retrosynthesis-xenobiology/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator API Test"
    assert data["retrosynthetic_pathway_plausibility_score"] != 0.0
    assert "item_profiles" in data
    assert "metric_traces" in data
    assert len(data["item_profiles"]) >= 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/metabolic-retrosynthesis-xenobiology/studies/{study_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == study_id

    list_resp = await async_client.get("/api/v1/metabolic-retrosynthesis-xenobiology/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
