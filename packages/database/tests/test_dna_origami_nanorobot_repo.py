"""Tests for DNAOrigamiRepository (Phase 149)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.dna_origami_nanorobot_repo import DNAOrigamiRepository


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
async def test_dna_origami_repo_lifecycle(async_db: AsyncSession):
    repo = DNAOrigamiRepository(async_db)

    campaign = await repo.create_campaign(
        nanorobot_name="Test DNA Nanorobot",
        geometry_type="Hexagonal Barrel",
        scaffold_type="M13mp18",
        staple_strands_count=180,
        predicted_melting_temp_c=62.5,
        folding_yield_percent=89.0,
        cargo_cavity_volume_nm3=1500.0,
        latch_trigger_affinity_nM=12.0,
    )
    assert campaign.id is not None

    await repo.add_staple(
        campaign_id=campaign.id,
        strand_index=1,
        sequence_5to3="AGCTAGCTAGCTAAGGTCCGATCGATCGA",
        length_nt=32,
        tm_celsius=62.4,
        crossover_count=3,
    )

    await repo.add_latch(
        campaign_id=campaign.id,
        target_biomarker="Nucleolin",
        aptamer_sequence="GGTGGTGGTGGTTGTGGTGGTGGTGG",
        opening_half_life_min=4.2,
        selectivity_ratio=25.0,
    )

    loaded = await repo.get_campaign_with_details(campaign.id)
    assert loaded is not None
    assert len(loaded.staples) == 1
    assert len(loaded.latches) == 1
