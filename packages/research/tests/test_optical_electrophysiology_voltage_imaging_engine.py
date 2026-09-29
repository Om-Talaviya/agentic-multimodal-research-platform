"""Tests for Phase 327: Autonomous Ultra-Fast kHz Genetically-Encoded Voltage Indicator (GEVI) Optical Electrophysiology Deconvolution Engine Engine."""

import pytest
from research.orchestration.optical_electrophysiology_voltage_imaging_engine import OpticalElectrophysiologyVoltageImagingEngine


def test_optical_electrophysiology_voltage_imaging_engine():
    engine = OpticalElectrophysiologyVoltageImagingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optical-electrophysiology-voltage",
        input_scale=1.0,
    )
    assert getattr(result, "spike_detection_temporal_jitter_microseconds") != 0
    assert getattr(result, "optical_signal_to_noise_ratio_snr") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
