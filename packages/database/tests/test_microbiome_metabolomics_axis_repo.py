"""Tests for Phase 182: Gut Microbiome-Host Metabolomics Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.microbiome_metabolomics_axis_repo import MicrobiomeMetabolomicsAxisRepository


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
async def test_microbiome_metabolomics_axis_repo_crud(async_db: AsyncSession):
    repo = MicrobiomeMetabolomicsAxisRepository(async_db)

    study = await repo.create_study(
        name="Cohort MB-9012 Test Study",
        cohort_sample_id="SMP-MB-9012",
        dietary_fiber_intake_g_day=32.0,
        firmicutes_bacteroidetes_ratio=1.85,
        total_scfa_concentration_mm=85.4,
        gut_barrier_integrity_score=0.91,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.cohort_sample_id == "SMP-MB-9012"

    taxa = await repo.add_taxa_abundance(
        study_id=study.id,
        taxon_name="Faecalibacterium prausnitzii",
        phylum="Firmicutes",
        relative_abundance_pct=8.5,
        butyrate_synthesis_pathway="butyryl-CoA:acetate CoA-transferase",
        mucosal_adherence_index=0.92,
    )
    await async_db.commit()

    assert taxa.id is not None
    assert taxa.taxon_name == "Faecalibacterium prausnitzii"

    scfa = await repo.add_scfa_kinetic(
        study_id=study.id,
        metabolite_name="Butyrate",
        lumen_concentration_mm=52.4,
        portal_vein_absorption_rate=2.15,
        anti_inflammatory_index=0.94,
    )
    await async_db.commit()

    assert scfa.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Cohort MB-9012 Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1