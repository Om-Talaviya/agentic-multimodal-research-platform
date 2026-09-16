"""
Tests for Phase 55: Computational Immunology Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.immunology_repo import ImmunologyRepository


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
async def test_immunology_repo_crud(async_session: AsyncSession):
    repo = ImmunologyRepository(async_session)

    # 1. Create Screen
    screen = await repo.create_screen(
        patient_id="PT-MEL-01",
        tumor_type="Melanoma",
        hla_alleles=["HLA-A*02:01", "HLA-B*07:02"],
        mutation_count=2,
    )
    assert screen.id is not None
    assert screen.patient_id == "PT-MEL-01"

    # 2. Add Epitopes
    epitopes = await repo.add_epitopes(
        screen.id,
        [
            {
                "gene_symbol": "BRAF",
                "mutation_variant": "V600E",
                "peptide_sequence": "EDLTVKIGD",
                "hla_allele": "HLA-A*02:01",
                "binding_ic50_nm": 32.5,
                "composite_priority_score": 0.92,
                "recommended_for_vaccine": True,
            },
            {
                "gene_symbol": "NRAS",
                "mutation_variant": "Q61K",
                "peptide_sequence": "ILDTAGKEEY",
                "hla_allele": "HLA-A*02:01",
                "binding_ic50_nm": 420.0,
                "composite_priority_score": 0.45,
                "recommended_for_vaccine": False,
            },
        ],
    )
    assert len(epitopes) == 2

    # 3. Create Vaccine Construct
    construct = await repo.create_vaccine_construct(
        screen_id=screen.id,
        construct_name="NeoVax-01",
        construct_type="mRNA_LNP",
        ordered_epitopes=["EDLTVKIGD"],
        linker_sequences=[],
        full_polyepitope_sequence="EDLTVKIGD",
    )
    assert construct.id is not None

    # 4. Get Screen with relationships
    fetched = await repo.get_screen(screen.id)
    assert fetched is not None
    assert len(fetched.epitopes) == 2
    assert len(fetched.vaccine_constructs) == 1
    assert fetched.top_candidates_count == 1
