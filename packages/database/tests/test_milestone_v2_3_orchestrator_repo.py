"""Tests for Phase 209: Milestone v2.3 Planetary Research Synthesis & Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v2_3_orchestrator_repo import MilestoneV23OrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v2_3_orchestrator_repository(db_session):
    repo = MilestoneV23OrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_209_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Milestone v2.3 Meta-Orchestrator",
        active_subsystems_count=209.0,
        global_synthesis_confidence_score=0.996,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 209 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_209_Verification"
    assert getattr(study, "active_subsystems_count") == 209.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Planetary Multi-Modal Cross-Domain Nexus [Phases 1-208 Synthesis]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Planetary Multi-Modal Cross-Domain Nexus [Phases 1-208 Synthesis]"

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
    assert fetched.name == "Study_209_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
