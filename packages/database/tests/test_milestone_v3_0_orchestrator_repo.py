"""Tests for Phase 266: Autonomous Milestone v3.0 Planetary Multi-Omics Research Synthesis & Centennial Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v3_0_orchestrator_repo import MilestoneV30OrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v3_0_orchestrator_repository(db_session):
    repo = MilestoneV30OrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_266_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="milestone-v3-0-orchestrator",
        centennial_planetary_orchestration_index=99.9,
        autonomous_pipeline_completion_rate_pct=100.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 266 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_266_Verification"
    assert getattr(study, "centennial_planetary_orchestration_index") == 99.9

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Centennial_Planetary_Synthesis_Campaign_v3_0",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Centennial_Planetary_Synthesis_Campaign_v3_0"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_266_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
