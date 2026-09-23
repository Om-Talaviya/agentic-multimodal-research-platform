"""
API integration tests for Phase 132: Viral Phylodynamics & Biosurveillance Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from api.dependencies import get_db
from main import app


@pytest.fixture
async def test_app():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_viral_phylodynamics_api_flow(test_app: AsyncClient):
    payload = {
        "pathogen_name": "Avian_Influenza_H5N1",
        "genome_type": "ssRNA(-)",
        "geographic_regions": ["Global", "North America", "South America"],
        "total_days": 60,
        "baseline_r0": 2.4,
        "lineages": [
            {
                "clade_name": "2.3.4.4b Clade",
                "pangolin_designation": "H5N1-2.3.4.4b",
                "who_label": "High Pathogenicity Avian Flu",
                "defining_mutations": ["HA:Q226L", "PB2:E627K"],
                "initial_proportion": 0.40,
                "fitness_advantage": 0.05,
            },
            {
                "clade_name": "Mammalian_Adapted_B3.13",
                "pangolin_designation": "H5N1-B3.13",
                "who_label": "Bovine Spillover Lineage",
                "defining_mutations": ["HA:Q226L", "PB2:M631L", "PB2:E627K"],
                "initial_proportion": 0.60,
                "fitness_advantage": 0.12,
            },
        ],
    }

    # 1. Run simulation
    res = await test_app.post("/api/v1/viral-phylodynamics/simulate", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "study_id" in data
    study_id = data["study_id"]
    assert data["lineages_count"] == 2
    assert data["effective_reproduction_number_rt"] > 0.5
    assert len(data["recommendations"]) > 0

    # 2. List studies
    list_res = await test_app.get("/api/v1/viral-phylodynamics/studies")
    assert list_res.status_code == 200
    studies = list_res.json()
    assert any(s["id"] == study_id for s in studies)

    # 3. Retrieve single study details
    get_res = await test_app.get(f"/api/v1/viral-phylodynamics/studies/{study_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["pathogen_name"] == "Avian_Influenza_H5N1"
    assert len(detail["lineages"]) == 2
    assert len(detail["fitness_profiles"]) == 2
