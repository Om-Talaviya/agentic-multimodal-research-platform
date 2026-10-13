"""Tests for Phase 471: Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker Repo."""

import pytest
from database.repositories.somatogenesis_hes7_clock_wavefront_repo import SomatogenesisHes7ClockWavefrontRepository


@pytest.mark.asyncio
async def test_somatogenesis_hes7_clock_wavefront_repository(db_session):
    repo = SomatogenesisHes7ClockWavefrontRepository(db_session)

    study = await repo.create_study(
        name="Study_471_Verification",
        target_specimen="Synthetic Presomitic Mesoderm (PSM) Microtissue Organoid with Oscillatory Hes7-Venus Reporter",
        analytical_modality="somatogenesis-clock-wavefront",
        clock_oscillation_periodicity_minutes=124.0,
        wavefront_propagation_velocity_um_per_hr=48.5,
        somite_boundary_sharpness_contrast_ratio=4.15,
        synchronization_kuramoto_order_parameter=0.942,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 471 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_471_Verification"
    assert study.clock_oscillation_periodicity_minutes == 124.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Hes7_Transcriptional_Delay_Traveling_Wave_Front",
        profile_category="Primary Step",
        quantitative_value=124.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Hes7_Transcriptional_Delay_Traveling_Wave_Front"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="clock_oscillation_periodicity_minutes",
        observed_value=124.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 124.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_471_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
