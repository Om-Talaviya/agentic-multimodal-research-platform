"""Tests for Phase 371: Autonomous Milestone v4.1 Planetary Frontier Bio-Computing Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v4_1_meta_orchestrator_repo import MilestoneV41MetaOrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v4_1_meta_orchestrator_repository(db_session):
    repo = MilestoneV41MetaOrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_371_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="milestone-v4-1-orchestrator",
        meta_orchestrator_cross_domain_synthesis_coherence_pct=99.99,
        planetary_scientific_workflow_dispatch_throughput_qps=52000.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 371 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_371_Verification"
    assert getattr(study, "meta_orchestrator_cross_domain_synthesis_coherence_pct") == 99.99

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Milestone_v4_1_Planetary_Bio_Computing_Synthesis_Mesh",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Milestone_v4_1_Planetary_Bio_Computing_Synthesis_Mesh"

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
    assert fetched.name == "Study_371_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
