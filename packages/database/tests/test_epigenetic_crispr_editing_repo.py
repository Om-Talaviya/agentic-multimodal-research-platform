"""Tests for EpigeneticCRISPRRepository (Phase 159)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.epigenetic_crispr_editing_repo import EpigeneticCRISPRRepository


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
async def test_epigenetic_crispr_editing_repo_lifecycle(async_db: AsyncSession):
    repo = EpigeneticCRISPRRepository(async_db)

    study = await repo.create_study(
        target_locus_name="B2M Promoter",
        catalytic_effector="dCas9-DNMT3A",
        guide_rna_sequence="GGCUAGCGUAGCUAGCUAGC",
        targeted_cpg_count=8,
        target_methylation_change_pct=85.0,
        transcriptional_repression_log2fc=-4.0,
        mitotic_memory_retention_days=40.0,
        off_target_epimutation_rate_pct=0.5,
    )
    assert study.id is not None

    await repo.add_cpg_profile(
        study_id=study.id,
        genomic_coordinate_bp=1000200,
        baseline_methylation_pct=5.0,
        post_edit_methylation_pct=90.0,
        bisulfite_read_depth=500,
    )

    await repo.add_off_target(
        study_id=study.id,
        off_target_locus="chr2:5000100",
        mismatch_count=3,
        methylation_drift_pct=1.0,
        safety_classification="PASS",
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.cpg_profiles) == 1
    assert len(loaded.off_targets) == 1
