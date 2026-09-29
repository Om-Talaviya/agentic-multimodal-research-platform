"""Tests for Phase 327: Autonomous Ultra-Fast kHz Genetically-Encoded Voltage Indicator (GEVI) Optical Electrophysiology Deconvolution Engine Repo."""

import pytest
from database.repositories.optical_electrophysiology_voltage_imaging_repo import OpticalElectrophysiologyVoltageImagingRepository


@pytest.mark.asyncio
async def test_optical_electrophysiology_voltage_imaging_repository(db_session):
    repo = OpticalElectrophysiologyVoltageImagingRepository(db_session)

    study = await repo.create_study(
        name="Study_327_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optical-electrophysiology-voltage",
        spike_detection_temporal_jitter_microseconds=180.0,
        optical_signal_to_noise_ratio_snr=28.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 327 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_327_Verification"
    assert getattr(study, "spike_detection_temporal_jitter_microseconds") == 180.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Somatosensory_Cortex_Layer_V_Pyramidal_Spike_Voltage_Array",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Somatosensory_Cortex_Layer_V_Pyramidal_Spike_Voltage_Array"

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
    assert fetched.name == "Study_327_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
