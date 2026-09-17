"""Tests for Metagenomic Pathogen Surveillance & AMR repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.amr_surveillance_repo import AMRSurveillanceRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_sample(async_session: AsyncSession):
    repo = AMRSurveillanceRepository(async_session)

    sample = await repo.create_sample(
        sample_name="Hospital ICU Wastewater",
        sample_type="WASTEWATER",
        collection_location="University Medical Center Wing C",
        total_reads_sequenced=12000000,
        pathogen_count=5,
        amr_genes_count=8,
        outbreak_risk_level="CRITICAL",
    )

    assert sample.id is not None
    assert sample.sample_name == "Hospital ICU Wastewater"

    fetched = await repo.get_sample(sample.id)
    assert fetched is not None
    assert fetched.outbreak_risk_level == "CRITICAL"


@pytest.mark.asyncio
async def test_add_pathogens_and_amr_genes(async_session: AsyncSession):
    repo = AMRSurveillanceRepository(async_session)

    sample = await repo.create_sample(
        sample_name="Air Bioaerosol Surveillance",
        sample_type="AIR_BIOAEROSOL",
        collection_location="Emergency Department Triage",
    )

    pathogens_data = [
        {
            "taxon_name": "Acinetobacter baumannii",
            "ncbi_taxid": 470,
            "relative_abundance_pct": 2.4,
            "read_depth": 24000,
            "pathogenicity_grade": "HIGH_CONSEQUENCE",
            "is_priority_pathogen": True,
        }
    ]

    pathogens = await repo.add_pathogens(sample.id, pathogens_data)
    assert len(pathogens) == 1
    assert pathogens[0].taxon_name == "Acinetobacter baumannii"

    amr_data = [
        {
            "gene_symbol": "blaOXA-23",
            "resistance_mechanism": "CARBAPENEMASE_HYDROLYSIS",
            "drug_class": "CARBAPENEMS",
            "identity_pct": 100.0,
            "coverage_pct": 100.0,
            "plasmid_mediated": True,
        }
    ]

    amr_genes = await repo.add_amr_genes(sample.id, amr_data)
    assert len(amr_genes) == 1
    assert amr_genes[0].gene_symbol == "blaOXA-23"

    fetched_pathogens = await repo.get_pathogens_by_sample(sample.id)
    assert len(fetched_pathogens) == 1

    fetched_amr = await repo.get_amr_genes_by_sample(sample.id)
    assert len(fetched_amr) == 1
