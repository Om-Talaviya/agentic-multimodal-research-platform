"""Tests for MilestoneV19Repository (Phase 161)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.milestone_v1_9_repo import MilestoneV19Repository


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
async def test_milestone_v1_9_repo_lifecycle(async_db: AsyncSession):
    repo = MilestoneV19Repository(async_db)

    orch = await repo.create_orchestration(
        cohort_study_name="TCGA Pan-Cancer Precision Atlas",
        milestone_version="v1.9",
        total_phases_integrated=161,
        patient_cohort_size=10000,
        clusters_identified_count=4,
        mean_hazard_ratio_separation=3.4,
        global_cross_modal_concordance=0.99,
    )
    assert orch.id is not None

    await repo.add_cluster(
        orchestration_id=orch.id,
        cluster_index=1,
        subtype_designation="Immune-Hot",
        dominant_pathway_alteration="dMMR",
        patient_percentage=28.0,
        median_progression_free_survival_months=34.0,
        recommended_therapy="Anti-PD-1",
    )

    await repo.add_efficacy_matrix(
        orchestration_id=orch.id,
        therapeutic_agent="TriTE",
        target_subtype="Immune-Hot",
        predicted_response_rate_pct=85.0,
        synergy_combination_score=0.92,
    )

    loaded = await repo.get_orchestration_with_details(orch.id)
    assert loaded is not None
    assert len(loaded.clusters) == 1
    assert len(loaded.efficacy_matrix) == 1
