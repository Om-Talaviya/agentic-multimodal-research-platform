"""Tests for Phase 300: Autonomous Tercentenary Milestone v3.5 Bio-Computational Discovery Matrix & Planetary Master Convergence Engine Repo."""

import pytest
from database.repositories.tercentenary_milestone_v3_5_orchestrator_repo import TercentenaryMilestoneV35OrchestratorRepository


@pytest.mark.asyncio
async def test_tercentenary_milestone_v3_5_orchestrator_repository(db_session):
    repo = TercentenaryMilestoneV35OrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_300_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="tercentenary-milestone-v3-5-orchestrator",
        tercentenary_planetary_convergence_index=99.99,
        autonomous_pipeline_completion_rate_pct=100.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 300 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_300_Verification"
    assert getattr(study, "tercentenary_planetary_convergence_index") == 99.99

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Tercentenary_Planetary_Master_Campaign_Phase_300",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Tercentenary_Planetary_Master_Campaign_Phase_300"

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
    assert fetched.name == "Study_300_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
