"""Tests for PROTACKineticsRepository (Phase 156)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.protac_ternary_complex_repo import PROTACKineticsRepository


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
async def test_protac_ternary_complex_repo_lifecycle(async_db: AsyncSession):
    repo = PROTACKineticsRepository(async_db)

    study = await repo.create_study(
        protac_compound_name="ARV-110",
        target_protein_name="Androgen Receptor",
        e3_ligase_name="VHL",
        linker_type="PEG3",
        cooperativity_alpha=4.5,
        dc50_nM=2.5,
        dmax_percent=95.0,
        hook_effect_threshold_uM=2.0,
    )
    assert study.id is not None

    await repo.add_e3_profile(
        study_id=study.id,
        domain_type="Warhead",
        kd_binary_nM=15.0,
        kd_ternary_nM=3.3,
        delta_g_formation_kcal_mol=-11.0,
    )

    await repo.add_degradation_point(
        study_id=study.id,
        protac_dose_nM=50.0,
        ternary_fraction=0.85,
        degradation_rate_pct=94.0,
        ubiquitination_flux=14.0,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.e3_profiles) == 1
    assert len(loaded.degradation_points) == 1
