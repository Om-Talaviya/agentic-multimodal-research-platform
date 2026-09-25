"""Tests for Phase 185: Tumor Neoantigen Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.neoantigen_hla_presentation_repo import NeoantigenHLAPresentationRepository


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
async def test_neoantigen_hla_presentation_repo_crud(async_db: AsyncSession):
    repo = NeoantigenHLAPresentationRepository(async_db)

    study = await repo.create_study(
        name="Patient MEL-402 Test Study",
        patient_tumor_id="TUMOR-MEL-402",
        patient_hla_alleles="HLA-A*02:01, HLA-A*24:02",
        somatic_mutations_analyzed_count=45,
        high_affinity_neoepitopes_count=8,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.patient_tumor_id == "TUMOR-MEL-402"

    candidate = await repo.add_peptide_candidate(
        study_id=study.id,
        gene_symbol="BRAF",
        mutation_syntax="p.V600E",
        wildtype_peptide="EDLTVKIGD",
        mutant_peptide_sequence="EDLTEKIGD",
        peptide_length=9,
        tcr_recognition_probability=0.92,
    )
    await async_db.commit()

    assert candidate.id is not None
    assert candidate.gene_symbol == "BRAF"

    pred = await repo.add_hla_prediction(
        study_id=study.id,
        peptide_sequence="EDLTEKIGD",
        hla_allele="HLA-A*02:01",
        binding_affinity_ic50_nm=14.5,
        presentation_percentile_rank=0.08,
        stability_half_life_hours=12.4,
        is_strong_binder=True,
    )
    await async_db.commit()

    assert pred.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Patient MEL-402 Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1