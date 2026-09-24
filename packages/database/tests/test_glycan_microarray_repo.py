"""Tests for GlycanMicroarrayRepository (Phase 148)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.glycan_microarray_repo import GlycanMicroarrayRepository


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
async def test_glycan_microarray_repo_lifecycle(async_db: AsyncSession):
    repo = GlycanMicroarrayRepository(async_db)

    screen = await repo.create_screen(
        target_lectin_name="Concanavalin A",
        organism_source="Canavalia ensiformis",
        array_spots_count=600,
        mean_signal_to_noise=45.2,
        primary_epitope_motif="High-Mannose Core",
        kd_apparent_nM=115.0,
    )
    assert screen.id is not None

    await repo.add_spot_record(
        screen_id=screen.id,
        glycan_iupac="Man(a1-3)[Man(a1-6)]Man",
        spot_index=0,
        fluorescence_rfu=55000.0,
        z_score=4.2,
        relative_affinity=1.0,
    )

    await repo.add_specificity_profile(
        screen_id=screen.id,
        glycan_motif="Trimannoside",
        enrichment_fold=7.5,
        p_value_log10=6.8,
        selectivity_index=0.92,
    )

    loaded = await repo.get_screen_with_details(screen.id)
    assert loaded is not None
    assert len(loaded.spot_records) == 1
    assert len(loaded.specificity_profiles) == 1
