"""Tests for Phase 179: circRNA Biogenesis Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.circrna_biogenesis_repo import CircRNABiogenesisRepository


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
async def test_circrna_biogenesis_repo_crud(async_db: AsyncSession):
    repo = CircRNABiogenesisRepository(async_db)

    study = await repo.create_study(
        name="CDR1as Test Study",
        host_gene_symbol="CDR1as",
        genomic_locus="chrX:139865339-139866824",
        exon_count=3,
        flanking_alu_elements_count=2,
        backsplice_efficiency_score=0.88,
        circular_form_half_life_hours=48.5,
        total_mirna_sponge_binding_sites=14,
        quaking_rbp_affinity_score=0.92,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.host_gene_symbol == "CDR1as"

    junction = await repo.add_backsplice_junction(
        study_id=study.id,
        junction_id="CDR1as_circ_exon3->exon1",
        donor_exon=3,
        acceptor_exon=1,
        junction_sequence="AGCTGAGCTAAG...CCATGTACG",
        junction_reads_ratio=0.34,
        flanking_repeat_match_score=0.91,
    )
    await async_db.commit()

    assert junction.id is not None
    assert junction.donor_exon == 3

    sponge = await repo.add_mirna_sponge_target(
        study_id=study.id,
        mirna_family="miR-7-5p",
        binding_site_start=45,
        binding_site_end=67,
        seed_match_type="8mer",
        binding_free_energy_kcal_mol=-24.5,
        inhibition_potency_score=0.94,
    )
    await async_db.commit()

    assert sponge.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "CDR1as Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1
