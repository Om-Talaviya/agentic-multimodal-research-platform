"""
Tests for Phase 62: Bioprocess Digital Twin Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.bioprocess_digital_twin_repo import BioprocessDigitalTwinRepository


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
async def test_bioprocess_repo_crud(async_session: AsyncSession):
    repo = BioprocessDigitalTwinRepository(async_session)

    # 1. Create Run
    run = await repo.create_run(
        run_name="Run-01",
        cell_line="CHO-K1",
        working_volume_liters=50.0,
    )
    assert run.id is not None

    # 2. Add Telemetry & Actions
    updated = await repo.add_telemetry_and_actions(
        run_id=run.id,
        telemetry_data=[
            {
                "time_hours": 0.0,
                "viable_cell_density_10e6_ml": 0.5,
                "cell_viability_pct": 99.0,
                "glucose_concentration_g_l": 6.0,
                "lactate_concentration_g_l": 0.2,
                "product_titer_g_l": 0.0,
            }
        ],
        actions_data=[
            {
                "time_hours": 72.0,
                "feed_rate_ml_h": 25.0,
            }
        ],
        final_titer=4.8,
    )
    assert updated is not None
    assert updated.final_titer_g_l == 4.8
    assert len(updated.telemetry_points) == 1
    assert len(updated.control_actions) == 1
