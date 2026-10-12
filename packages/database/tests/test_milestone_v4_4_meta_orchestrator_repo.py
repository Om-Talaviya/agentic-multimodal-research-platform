"""Tests for Phase 434: Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v4_4_meta_orchestrator_repo import MilestoneV44MetaOrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v4_4_meta_orchestrator_repository(db_session):
    repo = MilestoneV44MetaOrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_434_Verification",
        target_specimen="Planetary Multi-Scale Biophysical & Epitranscriptomic Synthesis Consortium",
        analytical_modality="milestone-v4-4-meta-orchestrator",
        cross_phase_coherence_index=0.998,
        dag_pipeline_throughput_jobs_per_s=185.0,
        multi_modal_synthesis_confidence=0.999,
        autonomous_discovery_convergence_tau=0.985,
        confidence_score=0.999,
        status="completed",
        summary_report="Phase 434 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_434_Verification"
    assert study.cross_phase_coherence_index == 0.998

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Grand_Synthesis_Consortium_Consensus_DAG",
        profile_category="Primary Step",
        quantitative_value=0.998,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Grand_Synthesis_Consortium_Consensus_DAG"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="cross_phase_coherence_index",
        observed_value=0.998,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.998

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_434_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
