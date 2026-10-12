"""Tests for Phase 442: Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator."""

import pytest
from research.orchestration.mammalian_circadian_clock_transcriptional_oscillator_engine import MammalianCircadianClockEngine


def test_mammalian_circadian_clock_transcriptional_oscillator_engine():
    engine = MammalianCircadianClockEngine()
    result = engine.analyze(
        target_specimen="Suprachiasmatic Nucleus (SCN) Single-Cell CLOCK:BMAL1 / PER:CRY Pacemaker Circuit",
        analytical_modality="circadian-ttfl-oscillator",
        input_scale=1.0,
    )

    assert result.target_specimen == "Suprachiasmatic Nucleus (SCN) Single-Cell CLOCK:BMAL1 / PER:CRY Pacemaker Circuit"
    assert result.confidence_score >= 0.95
    assert result.free_running_period_tau_hours > 0.0
    assert result.oscillation_amplitude_per2_mrna_ratio > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Mammalian Circadian" in result.summary_report
