"""
Tests for Phase 61: Rare Disease HPO Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.rare_disease_hpo_repo import RareDiseaseHPORepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_rare_disease_repo_crud(async_session: AsyncSession):
    repo = RareDiseaseHPORepository(async_session)

    # 1. Create Case
    case = await repo.create_case(
        case_number="CASE-001",
        patient_id="PT-001",
        clinical_summary="Infantile spasms",
    )
    assert case.id is not None

    # 2. Add Phenotypes & Matches
    updated = await repo.add_phenotypes_and_matches(
        case_id=case.id,
        phenotypes_data=[
            {"hpo_id": "HP:0001250", "term_name": "Seizures"}
        ],
        candidate_genes_data=[
            {
                "gene_symbol": "SCN1A",
                "disease_name": "Dravet Syndrome",
                "semantic_similarity_score": 0.95,
                "is_top_match": True,
            }
        ],
    )
    assert updated is not None
    assert updated.total_phenotypes_mapped == 1
    assert len(updated.phenotypes) == 1
    assert len(updated.candidate_genes) == 1
