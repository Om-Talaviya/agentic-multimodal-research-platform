"""Tests for Phase 442: Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator Repo."""

import pytest
from database.repositories.mammalian_circadian_clock_transcriptional_oscillator_repo import MammalianCircadianClockRepository


@pytest.mark.asyncio
async def test_mammalian_circadian_clock_transcriptional_oscillator_repository(db_session):
    repo = MammalianCircadianClockRepository(db_session)

    study = await repo.create_study(
        name="Study_442_Verification",
        target_specimen="Suprachiasmatic Nucleus (SCN) Single-Cell CLOCK:BMAL1 / PER:CRY Pacemaker Circuit",
        analytical_modality="circadian-ttfl-oscillator",
        free_running_period_tau_hours=24.15,
        oscillation_amplitude_per2_mrna_ratio=4.82,
        phase_response_shift_hours=-2.4,
        limit_cycle_bifurcation_stability=0.978,
        confidence_score=0.987,
        status="completed",
        summary_report="Phase 442 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_442_Verification"
    assert study.free_running_period_tau_hours == 24.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CLOCK_BMAL1_EBox_Binding_Occupancy",
        profile_category="Primary Step",
        quantitative_value=24.15,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "CLOCK_BMAL1_EBox_Binding_Occupancy"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="free_running_period_tau_hours",
        observed_value=24.15,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 24.15

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_442_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
