"""Tests for Phase 181: Rare Disease Deep Phenotyping Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.rare_disease_hpo_phenotyping_repo import RareDiseaseHPOPhenotypingRepository


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
async def test_rare_disease_hpo_phenotyping_repo_crud(async_db: AsyncSession):
    repo = RareDiseaseHPOPhenotypingRepository(async_db)

    study = await repo.create_study(
        name="Marfan Syndrome Test Study",
        patient_cohort_id="PT-RD-8841",
        primary_clinical_presentation="Aortic root aneurysm and ectopia lentis",
        extracted_hpo_count=5,
        top_omim_disease_candidate="Marfan Syndrome",
        semantic_similarity_resnik_score=0.885,
        causal_gene_symbol="FBN1",
    )
    await async_db.commit()

    assert study.id is not None
    assert study.patient_cohort_id == "PT-RD-8841"

    term = await repo.add_hpo_term(
        study_id=study.id,
        hpo_id="HP:0002650",
        hpo_label="Aortic root aneurysm",
        information_content_score=8.45,
        clinical_severity_weight=2.5,
        organ_system_category="Cardiovascular",
    )
    await async_db.commit()

    assert term.id is not None
    assert term.hpo_id == "HP:0002650"

    match = await repo.add_omim_match(
        study_id=study.id,
        omim_id="OMIM:154700",
        disease_name="Marfan Syndrome",
        causal_genes="FBN1",
        phenomizer_p_value=0.00012,
        jaccard_similarity_score=0.82,
        matching_terms_count=4,
    )
    await async_db.commit()

    assert match.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Marfan Syndrome Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1