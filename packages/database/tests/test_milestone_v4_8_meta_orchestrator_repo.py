"""Tests for Phase 518: Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine Repo."""

import pytest
from database.repositories.milestone_v4_8_meta_orchestrator_repo import MilestoneV48MetaOrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v4_8_meta_orchestrator_repository(db_session):
    repo = MilestoneV48MetaOrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Study_518_Verification",
        target_specimen="Integrated Milestone v4.8 Synthetic Biofoundry, MRFM Quantum Imaging, CAST Transposase & Living Bioelectronics Suite",
        analytical_modality="planetary-v4-8-meta-orchestration",
        synthetic_biofoundry_orchestration_coherence=0.997,
        xenobiotic_chassis_cellular_compatibility_tau=0.993,
        cross_engine_federated_convergence_ratio=0.996,
        global_synthesis_confidence_score=0.999,
        confidence_score=0.999,
        status="completed",
        summary_report="Phase 518 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_518_Verification"
    assert study.synthetic_biofoundry_orchestration_coherence == 0.997

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Grand_Milestone_V4_8_Planetary_Biofoundry_Synthesis",
        profile_category="Primary Step",
        quantitative_value=0.997,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Grand_Milestone_V4_8_Planetary_Biofoundry_Synthesis"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="synthetic_biofoundry_orchestration_coherence",
        observed_value=0.997,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.997

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_518_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
