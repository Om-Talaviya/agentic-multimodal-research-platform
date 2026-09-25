"""Tests for Phase 178: ADC DAR Optimization Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.adc_dar_optimization_repo import ADCDAROptimizationRepository


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_adc_dar_optimization_repo_crud(async_db: AsyncSession):
    repo = ADCDAROptimizationRepository(async_db)

    study = await repo.create_study(
        name="Test Trastuzumab-MMAE Study",
        antibody_name="Trastuzumab",
        payload_name="MMAE",
        target_dar=4.0,
        calculated_mean_dar=3.85,
        aggregation_propensity_score=0.12,
        hydrophobicity_index=2.45,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.target_dar == 4.0

    species = await repo.add_species_distribution(
        study_id=study.id,
        dar_species=4,
        molar_fraction=45.2,
        retention_time_min=18.4,
        mass_shift_da=2872.0,
        relative_clearance_rate=1.88,
    )
    await async_db.commit()

    assert species.id is not None
    assert species.dar_species == 4

    metric = await repo.add_aggregation_metric(
        study_id=study.id,
        incubation_hours=24.0,
        monomer_percentage=97.8,
        high_molecular_weight_pct=1.8,
        low_molecular_weight_pct=0.4,
        turbidity_od350=0.035,
    )
    await async_db.commit()

    assert metric.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Test Trastuzumab-MMAE Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1
