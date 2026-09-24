"""Tests for CFPSTXTLRepository (Phase 157)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.cfps_txtl_kinetics_repo import CFPSTXTLRepository


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
async def test_cfps_txtl_repo_lifecycle(async_db: AsyncSession):
    repo = CFPSTXTLRepository(async_db)

    study = await repo.create_study(
        target_protein_name="GFP Reporter",
        extract_system_type="E. coli BL21",
        reaction_mode="Batch",
        reaction_time_hours=8.0,
        final_protein_yield_mg_ml=1.85,
        transcription_rate_nt_s=40.0,
        translation_rate_aa_s=1.5,
        energy_regeneration_efficiency=0.88,
    )
    assert study.id is not None

    await repo.add_yield_curve_point(
        study_id=study.id,
        time_elapsed_hours=4.0,
        mrna_concentration_uM=10.5,
        protein_concentration_mg_ml=1.2,
        ribosome_active_fraction=0.85,
    )

    await repo.add_substrate_depletion(
        study_id=study.id,
        substrate_name="ATP",
        initial_concentration_mM=4.0,
        final_concentration_mM=1.5,
        consumption_rate_mM_h=0.3,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.yield_curves) == 1
    assert len(loaded.substrates) == 1
