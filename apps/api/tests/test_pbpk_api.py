"""
Integration tests for Nanomedicine PBPK REST API (Phase 60).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_pbpk_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Simulation
        res = await client.post(
            "/api/v1/pbpk-nanomedicine/simulations",
            json={
                "formulation_name": "LNP-Test-API",
                "carrier_type": "Lipid Nanoparticle (LNP)",
                "hydrodynamic_diameter_nm": 80.0,
                "zeta_potential_mv": -2.5,
                "pegylation_density_pct": 2.0,
                "dose_mg_kg": 1.5,
                "tumor_epr_permeability_index": 0.9,
            },
        )
        assert res.status_code == 201
        data = res.json()
        sim_id = data["id"]
        assert len(data["compartments"]) == 7

        # 2. Get Simulation Detail
        get_res = await client.get(f"/api/v1/pbpk-nanomedicine/simulations/{sim_id}")
        assert get_res.status_code == 200
        assert get_res.json()["formulation_name"] == "LNP-Test-API"

        # 3. List Simulations
        list_res = await client.get("/api/v1/pbpk-nanomedicine/simulations")
        assert list_res.status_code == 200
        assert any(s["id"] == sim_id for s in list_res.json())
