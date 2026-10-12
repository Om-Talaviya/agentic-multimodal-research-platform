"""Tests for Phase 425: Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

import pytest
from research.orchestration.cfps_microfluidic_oscillator_engine import CfpsMicrofluidicOscillatorEngine


def test_cfps_microfluidic_oscillator_engine():
    engine = CfpsMicrofluidicOscillatorEngine()
    result = engine.analyze(
        target_specimen="Microfluidic Droplet Array with Repressilator TX-TL Reaction",
        analytical_modality="cfps-microfluidic-oscillator",
        input_scale=1.0,
    )

    assert result.target_specimen == "Microfluidic Droplet Array with Repressilator TX-TL Reaction"
    assert result.confidence_score >= 0.95
    assert result.oscillation_period_minutes > 0.0
    assert result.fluorescent_reporter_amplitude_rfu > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cell-Free Protein T" in result.summary_report
