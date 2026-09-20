"""
Unit tests for Phase 108: Organ-on-a-Chip Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.organ_chip_repo import OrganChipRepository

@pytest.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_organ_chip_repo_crud(async_db: AsyncSession):
    repo = OrganChipRepository(async_db)

    # 1. Create simulation
    sim = await repo.create_simulation(
        chip_name="BBB-Chip-01",
        organ_type="BLOOD_BRAIN_BARRIER",
        fluid_viscosity_cp=1.0,
        perfusion_flow_rate_ul_min=30.0,
        shear_stress_dyn_cm2=5.2,
        endothelial_barrier_integrity_teer=1250.0
    )
    assert sim.id is not None
    assert sim.chip_name == "BBB-Chip-01"

    # 2. Add channels
    channels = await repo.add_channels(
        simulation_id=sim.id,
        channels_data=[
            {
                "channel_name": "Vascular_Apical",
                "width_um": 500.0,
                "height_um": 150.0,
                "length_mm": 20.0,
                "flow_velocity_mm_s": 3.2,
                "reynolds_number": 0.08
            }
        ]
    )
    assert len(channels) == 1

    # 3. Add shear profiles
    profiles = await repo.add_shear_profiles(
        simulation_id=sim.id,
        profiles_data=[
            {
                "axial_position_mm": 5.0,
                "wall_shear_stress": 5.2,
                "drug_permeation_pct": 12.0,
                "tight_junction_expression": 95.0
            }
        ]
    )
    assert len(profiles) == 1

    # 4. Fetch hydrated
    fetched = await repo.get_simulation(sim.id)
    assert fetched is not None
    assert len(fetched.channels) == 1
    assert len(fetched.shear_profiles) == 1
