"""Tests for mRNACodonRepository (Phase 153)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.mrna_codon_optimization_repo import mRNACodonRepository


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
async def test_mrna_codon_optimization_repo_lifecycle(async_db: AsyncSession):
    repo = mRNACodonRepository(async_db)

    campaign = await repo.create_campaign(
        target_protein_name="Spike Antigen",
        expression_host="Homo sapiens",
        original_cai=0.70,
        optimized_cai=0.96,
        gc_content_percent=57.5,
        mfe_secondary_struct_kcal_mol=-320.0,
        uridine_depletion_percent=35.0,
        translation_efficiency_score=0.94,
    )
    assert campaign.id is not None

    await repo.add_variant(
        campaign_id=campaign.id,
        variant_rank=1,
        mrna_sequence="AUGUUCGUG...",
        pareto_fitness_score=0.95,
        ribosome_dwell_time_ms=30.0,
        immunogenicity_risk_score=0.1,
    )

    await repo.add_cai_point(
        campaign_id=campaign.id,
        codon_position=1,
        codon_triplet="AUG",
        amino_acid="M",
        relative_adaptiveness=1.0,
    )

    loaded = await repo.get_campaign_with_details(campaign.id)
    assert loaded is not None
    assert len(loaded.variants) == 1
    assert len(loaded.cai_profiles) == 1
