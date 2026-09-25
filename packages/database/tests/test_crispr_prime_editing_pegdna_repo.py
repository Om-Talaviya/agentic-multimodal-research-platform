"""Tests for Phase 180: CRISPR Prime Editing pegRNA Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.crispr_prime_editing_pegdna_repo import CRISPRPrimeEditingPegDNARepository


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
async def test_crispr_prime_editing_pegdna_repo_crud(async_db: AsyncSession):
    repo = CRISPRPrimeEditingPegDNARepository(async_db)

    study = await repo.create_study(
        name="HBB Sickle Cell Test Study",
        target_gene="HBB",
        intended_mutation_type="point_substitution",
        pbs_length_nt=13,
        rtt_length_nt=15,
        predicted_prime_editing_efficiency=0.68,
        indel_byproduct_frequency=0.035,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.target_gene == "HBB"

    design = await repo.add_pegdna_design(
        study_id=study.id,
        candidate_id="pegRNA_HBB_PBS13_RTT15_v1",
        spacer_sequence_20nt="GACAGGTACGGCTATGCCA",
        pbs_sequence="CGTTAGCTATGC",
        rtt_sequence_with_edit="GCAATTTGGTACAGTT",
        tevpre_structural_motif="tevpre_hairpin_epegRNA",
        deep_pe_score=0.84,
        melting_temp_pbs_celsius=38.5,
    )
    await async_db.commit()

    assert design.id is not None
    assert design.candidate_id == "pegRNA_HBB_PBS13_RTT15_v1"

    metric = await repo.add_flap_metric(
        study_id=study.id,
        flap_position_nt=3,
        gibbs_free_energy_edited_flap_kcal=-20.3,
        gibbs_free_energy_unmodified_flap_kcal=-17.5,
        fen1_endonuclease_cleavage_rate=0.54,
        incorporation_probability=0.71,
    )
    await async_db.commit()

    assert metric.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "HBB Sickle Cell Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1
