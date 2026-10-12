"""Tests for Phase 439: Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator Repo."""

import pytest
from database.repositories.bacterial_chemotaxis_run_tumble_simulator_repo import BacterialChemotaxisSimulatorRepository


@pytest.mark.asyncio
async def test_bacterial_chemotaxis_run_tumble_simulator_repository(db_session):
    repo = BacterialChemotaxisSimulatorRepository(db_session)

    study = await repo.create_study(
        name="Study_439_Verification",
        target_specimen="E. coli K-12 Motile Swarm in Microfluidic Attractant/Repellent Gradient",
        analytical_modality="chemotaxis-run-tumble",
        run_duration_mean_seconds=1.25,
        tumble_frequency_hz=0.45,
        chemotactic_drift_velocity_um_per_s=8.42,
        chey_p_phosphorylation_equilibrium=0.32,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 439 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_439_Verification"
    assert study.run_duration_mean_seconds == 1.25

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Flagellar_Motor_CW_CCW_Stochastic_Switch",
        profile_category="Primary Step",
        quantitative_value=1.25,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Flagellar_Motor_CW_CCW_Stochastic_Switch"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="chemotactic_drift_velocity_um_per_s",
        observed_value=1.25,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.25

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_439_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
