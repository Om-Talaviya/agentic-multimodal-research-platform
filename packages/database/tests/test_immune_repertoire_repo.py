"""
Unit tests for Phase 104: Immune Repertoire Database Repository.
"""
import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.immune_repertoire_repo import ImmuneRepertoireRepository

@pytest.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_immune_repertoire_repo_crud(async_db: AsyncSession):
    repo = ImmuneRepertoireRepository(async_db)

    # 1. Create repertoire
    repertoire = await repo.create_repertoire(
        sample_name="PBMC-Donor-01",
        organism="Homo sapiens",
        chain_type="TCR_ALPHA_BETA",
        total_cells=1000,
        shannon_entropy=2.45,
        gini_simpson_index=0.88,
        clonality_score=0.25
    )
    assert repertoire.id is not None
    assert repertoire.sample_name == "PBMC-Donor-01"

    # 2. Add clonotypes
    clonotypes = await repo.add_clonotypes(
        repertoire_id=repertoire.id,
        clonotypes_data=[
            {
                "cdr3_aa": "CASSLAPGATNEKLFF",
                "v_gene": "TRBV7-2*01",
                "j_gene": "TRBJ1-4*01",
                "count": 500,
                "frequency": 0.5,
                "is_productive": True,
                "antigen_specificity": "EBV_BMLF1"
            },
            {
                "cdr3_aa": "CASSLIGVSSYNEQFF",
                "v_gene": "TRBV19*01",
                "j_gene": "TRBJ2-1*01",
                "count": 500,
                "frequency": 0.5,
                "is_productive": True,
                "antigen_specificity": "CMV_pp65"
            }
        ]
    )
    assert len(clonotypes) == 2

    # 3. Add VDJ pairings
    pairings = await repo.add_vdj_pairings(
        repertoire_id=repertoire.id,
        pairings_data=[
            {"v_family": "TRBV7-2", "j_family": "TRBJ1-4", "pairing_frequency": 0.5, "cdr3_length": 16},
            {"v_family": "TRBV19", "j_family": "TRBJ2-1", "pairing_frequency": 0.5, "cdr3_length": 16}
        ]
    )
    assert len(pairings) == 2

    # 4. Get hydrated repertoire
    fetched = await repo.get_repertoire(repertoire.id)
    assert fetched is not None
    assert len(fetched.clonotypes) == 2
    assert len(fetched.vdj_pairings) == 2
    assert fetched.clonotype_count == 2
