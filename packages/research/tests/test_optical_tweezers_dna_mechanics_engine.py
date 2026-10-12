"""Tests for Phase 416: Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

import pytest
from research.orchestration.optical_tweezers_dna_mechanics_engine import OpticalTweezersDnaMechanicsEngine


def test_optical_tweezers_dna_mechanics_engine():
    engine = OpticalTweezersDnaMechanicsEngine()
    result = engine.analyze(
        target_specimen="Single-Molecule Lambda-DNA Tether with RecA Nucleoprotein",
        analytical_modality="optical-tweezers",
        input_scale=1.0,
    )

    assert result.target_specimen == "Single-Molecule Lambda-DNA Tether with RecA Nucleoprotein"
    assert result.confidence_score >= 0.95
    assert result.overstretching_transition_force_pN > 0.0
    assert result.persistence_length_nm > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Optical Tweezers DN" in result.summary_report
