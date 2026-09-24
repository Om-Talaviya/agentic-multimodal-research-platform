"""Tests for SpatialFluxRepository (Phase 150)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.single_cell_spatial_flux_repo import SpatialFluxRepository


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
async def test_single_cell_spatial_flux_repo_lifecycle(async_db: AsyncSession):
    repo = SpatialFluxRepository(async_db)

    study = await repo.create_study(
        tissue_sample_id="TME-GBM-001",
        organ_context="Glioblastoma",
        single_cells_simulated=1500,
        mean_glycolytic_flux=17.5,
        mean_oxphos_flux=10.2,
        lactate_secretion_rate=30.1,
        atp_generation_rate=45.0,
    )
    assert study.id is not None

    await repo.add_flux_rate(
        study_id=study.id,
        reaction_id="HEX1",
        reaction_name="Hexokinase",
        subsystem="Glycolysis",
        flux_rate_mmol_gdw_h=18.0,
        shadow_price=-0.05,
    )

    await repo.add_microdomain(
        study_id=study.id,
        domain_name="Perivascular",
        radial_distance_um=20.0,
        oxygen_concentration_uM=50.0,
        glucose_concentration_mM=5.0,
        warburg_phenotype_score=0.3,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.flux_rates) == 1
    assert len(loaded.microdomains) == 1
