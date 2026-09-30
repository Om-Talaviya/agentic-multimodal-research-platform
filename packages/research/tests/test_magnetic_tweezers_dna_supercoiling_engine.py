"""Tests for Phase 401: Autonomous Magnetic Tweezers Single-Molecule DNA Supercoiling Engine Engine."""

import pytest
from research.orchestration.magnetic_tweezers_dna_supercoiling_engine import MagneticTweezersDnaSupercoilingEngine


def test_magnetic_tweezers_dna_supercoiling_engine():
    engine = MagneticTweezersDnaSupercoilingEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="magnetic-tweezers-dna-supercoiling",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "dna_extension_change_nm_per_turn") > 0
    assert getattr(result, "topoisomerase_relaxation_unlinking_rate_hz") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 401" in result.summary_report
