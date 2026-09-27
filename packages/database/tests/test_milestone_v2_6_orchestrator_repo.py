"""Tests for Phase 238: Autonomous Milestone v2.6 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v2_6_orchestrator_repo import MilestoneV26OrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v2_6_orchestrator_repository(db_session):
    repo = MilestoneV26OrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_238_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="milestone-v2-6-orchestrator",
        system_orchestration_synergy_index=99.9,
        autonomous_workflow_throughput_qps=2150.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 238 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_238_Verification"
    assert getattr(study, "system_orchestration_synergy_index") == 99.9

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Global_Planetary_Synthesis_Campaign_Gen36",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Global_Planetary_Synthesis_Campaign_Gen36"

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
    assert fetched.name == "Study_238_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
