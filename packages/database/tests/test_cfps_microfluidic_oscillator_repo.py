"""Tests for Phase 425: Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator Repo."""

import pytest
from database.repositories.cfps_microfluidic_oscillator_repo import CfpsMicrofluidicOscillatorRepository


@pytest.mark.asyncio
async def test_cfps_microfluidic_oscillator_repository(db_session):
    repo = CfpsMicrofluidicOscillatorRepository(db_session)

    study = await repo.create_study(
        name="Study_425_Verification",
        target_specimen="Microfluidic Droplet Array with Repressilator TX-TL Reaction",
        analytical_modality="cfps-microfluidic-oscillator",
        oscillation_period_minutes=124.0,
        fluorescent_reporter_amplitude_rfu=4850.0,
        reaction_dwell_stability_score=0.965,
        damping_decay_coefficient=0.042,
        confidence_score=0.983,
        status="completed",
        summary_report="Phase 425 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_425_Verification"
    assert study.oscillation_period_minutes == 124.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Repressilator_Negative_Feedback_Limit_Cycle",
        profile_category="Primary Step",
        quantitative_value=124.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Repressilator_Negative_Feedback_Limit_Cycle"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="oscillation_period_minutes",
        observed_value=124.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 124.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_425_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
