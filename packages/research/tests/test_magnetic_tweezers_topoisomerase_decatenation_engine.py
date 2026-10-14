"""Tests for Phase 484: Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

import pytest
from research.orchestration.magnetic_tweezers_topoisomerase_decatenation_engine import MagneticTweezersTopoisomeraseDecatenationEngine


def test_magnetic_tweezers_topoisomerase_decatenation_engine():
    engine = MagneticTweezersTopoisomeraseDecatenationEngine()
    result = engine.analyze(
        target_specimen="Tethered Braided DNA Minicircle Pair with Purified Human Topoisomerase II-alpha in Flow Cell",
        analytical_modality="magnetic-tweezers-decatenation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Tethered Braided DNA Minicircle Pair with Purified Human Topoisomerase II-alpha in Flow Cell"
    assert result.confidence_score >= 0.95
    assert result.decatenation_catalytic_rate_per_sec != 0.0
    assert result.atp_hydrolysis_coupling_ratio != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Molecule Mag" in result.summary_report
