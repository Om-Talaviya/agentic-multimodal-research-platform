"""Tests for Phase 444: Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator Repo."""

import pytest
from database.repositories.optogenetic_action_potential_trajectory_repo import OptogeneticActionPotentialRepository


@pytest.mark.asyncio
async def test_optogenetic_action_potential_trajectory_repository(db_session):
    repo = OptogeneticActionPotentialRepository(db_session)

    study = await repo.create_study(
        name="Study_444_Verification",
        target_specimen="Channelrhodopsin-2 (ChR2) Expressing Cortical Pyramidal Neurons under 470nm Pulsed Blue Light",
        analytical_modality="optogenetic-membrane-depolarization",
        membrane_depolarization_rate_mv_per_ms=18.4,
        action_potential_firing_fidelity=0.982,
        photocurrent_amplitude_pA=840.0,
        channel_closing_decay_tau_off_ms=11.2,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 444 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_444_Verification"
    assert study.membrane_depolarization_rate_mv_per_ms == 18.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Photocurrent_Inward_Sodium_Flux_Step",
        profile_category="Primary Step",
        quantitative_value=18.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Photocurrent_Inward_Sodium_Flux_Step"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="membrane_depolarization_rate_mv_per_ms",
        observed_value=18.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 18.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_444_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
