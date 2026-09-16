"""
Tests for Phase 60: Nanomedicine PBPK Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.pbpk_nanomedicine_repo import NanomedicinePBPKRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_pbpk_repo_crud(async_session: AsyncSession):
    repo = NanomedicinePBPKRepository(async_session)

    # 1. Create Simulation
    sim = await repo.create_simulation(
        formulation_name="LNP-Test-01",
        carrier_type="Lipid Nanoparticle (LNP)",
        hydrodynamic_diameter_nm=85.0,
    )
    assert sim.id is not None

    # 2. Add Compartments & Clearance
    updated = await repo.add_compartments_and_clearance(
        simulation_id=sim.id,
        compartments_data=[
            {
                "organ_name": "Plasma",
                "auc_ug_h_ml": 450.0,
                "cmax_ug_ml": 38.0,
                "tmax_hours": 0.25,
            }
        ],
        clearance_data=[
            {
                "pathway_name": "Hepatic MPS",
                "clearance_fraction_pct": 65.0,
                "half_life_hours": 18.0,
            }
        ],
    )
    assert updated is not None
    assert len(updated.compartments) == 1
    assert len(updated.clearance_pathways) == 1
