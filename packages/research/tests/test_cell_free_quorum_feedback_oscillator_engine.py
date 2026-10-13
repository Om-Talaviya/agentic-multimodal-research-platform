"""Tests for Phase 454: Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

import pytest
from research.orchestration.cell_free_quorum_feedback_oscillator_engine import CellFreeQuorumFeedbackOscillatorEngine


def test_cell_free_quorum_feedback_oscillator_engine():
    engine = CellFreeQuorumFeedbackOscillatorEngine()
    result = engine.analyze(
        target_specimen="Micro-Emulsion Lipid Vesicles with LuxI/LuxR Synthetic Transcriptional Auto-Inducer Network",
        analytical_modality="cell-free-quorum-oscillator",
        input_scale=1.0,
    )

    assert result.target_specimen == "Micro-Emulsion Lipid Vesicles with LuxI/LuxR Synthetic Transcriptional Auto-Inducer Network"
    assert result.confidence_score >= 0.95
    assert result.quorum_oscillation_periodicity_hours != 0.0
    assert result.ahl_autoinducer_diffusion_flux_umol_cm2_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Cell-Free" in result.summary_report
