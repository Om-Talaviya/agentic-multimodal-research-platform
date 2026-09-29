"""Tests for Phase 353: Autonomous Whole-Brain 2-Photon Calcium Imaging Neural Circuit Dynamics & Attractor Network Modeler Repo."""

import pytest
from database.repositories.two_photon_neural_dynamics_repo import TwoPhotonNeuralDynamicsRepository


@pytest.mark.asyncio
async def test_two_photon_neural_dynamics_repository(db_session):
    repo = TwoPhotonNeuralDynamicsRepository(db_session)

    study = await repo.create_study(
        name="Study_353_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="two-photon-neural-dynamics",
        spike_inference_temporal_precision_ms=4.5,
        neural_population_attractor_coherence_pct=96.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 353 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_353_Verification"
    assert getattr(study, "spike_inference_temporal_precision_ms") == 4.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Visual_Cortex_V1_Orientation_Column_Attractor_Manifold",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Visual_Cortex_V1_Orientation_Column_Attractor_Manifold"

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
    assert fetched.name == "Study_353_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
