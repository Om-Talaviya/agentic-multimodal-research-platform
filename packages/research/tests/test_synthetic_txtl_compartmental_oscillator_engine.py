"""Tests for Phase 488: Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

import pytest
from research.orchestration.synthetic_txtl_compartmental_oscillator_engine import SyntheticTxtlCompartmentalOscillatorEngine


def test_synthetic_txtl_compartmental_oscillator_engine():
    engine = SyntheticTxtlCompartmentalOscillatorEngine()
    result = engine.analyze(
        target_specimen="Continuous Microfluidic Droplet-Exchanged E. coli Cell-Free Expression Matrix with Repressilator Circuit",
        analytical_modality="txtl-compartmental-oscillator",
        input_scale=1.0,
    )

    assert result.target_specimen == "Continuous Microfluidic Droplet-Exchanged E. coli Cell-Free Expression Matrix with Repressilator Circuit"
    assert result.confidence_score >= 0.95
    assert result.oscillation_periodicity_hours != 0.0
    assert result.peak_to_trough_amplitude_fold_change != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cell-Free Compartme" in result.summary_report
