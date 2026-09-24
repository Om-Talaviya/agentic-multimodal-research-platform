"""Tests for AptamerEvolutionRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.aptamer_evolution_repo import AptamerEvolutionRepository


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
async def test_aptamer_evolution_repo_lifecycle(async_db: AsyncSession):
    repo = AptamerEvolutionRepository(async_db)

    camp = await repo.create_campaign(
        target_protein_name="Human Thrombin",
        aptamer_type="ssDNA",
        initial_pool_size=1000000,
        selection_rounds=8,
        top_kd_nanomolar=5.2,
        consensus_motif="GGTTGGTGTGGTTGG",
    )
    assert camp.id is not None

    await repo.add_round_sequence(
        campaign_id=camp.id,
        round_number=8,
        sequence_string="GGTTGGTGTGGTTGG",
        enrichment_fold=420.5,
        secondary_structure_dot_bracket="((((....))))",
        free_energy_kcal_mol=-12.4,
    )

    await repo.add_binding_record(
        campaign_id=camp.id,
        aptamer_lead_id="TBA-15-Lead",
        target_epitope_residues="Arg73, Lys77, Arg75",
        kd_nanomolar=5.2,
        off_target_selectivity_ratio=85.0,
    )

    loaded = await repo.get_campaign_with_details(camp.id)
    assert loaded is not None
    assert len(loaded.round_sequences) == 1
    assert len(loaded.binding_records) == 1
    assert loaded.binding_records[0].kd_nanomolar == 5.2
