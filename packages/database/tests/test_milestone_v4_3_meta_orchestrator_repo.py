"""Tests for Phase 413: Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v4_3_meta_orchestrator_repo import MilestoneV43MetaOrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v4_3_meta_orchestrator_repository(db_session):
    repo = MilestoneV43MetaOrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_413_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="milestone-v4-3-meta-orchestration",
        global_system_synthesis_coherence_index=0.999,
        cross_modal_autonomous_research_throughput_fold=185.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 413 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_413_Verification"
    assert getattr(study, "global_system_synthesis_coherence_index") == 0.999

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Milestone_v4_3_Planetary_Bioscience_Autonomous_OS_Architecture",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Milestone_v4_3_Planetary_Bioscience_Autonomous_OS_Architecture"

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
    assert fetched.name == "Study_413_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
