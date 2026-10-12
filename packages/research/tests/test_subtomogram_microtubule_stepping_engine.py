"""Tests for Phase 418: Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

import pytest
from research.orchestration.subtomogram_microtubule_stepping_engine import SubtomogramMicrotubuleSteppingEngine


def test_subtomogram_microtubule_stepping_engine():
    engine = SubtomogramMicrotubuleSteppingEngine()
    result = engine.analyze(
        target_specimen="Axonemal 13-Protofilament Microtubule with Kinesin-1 Dimers",
        analytical_modality="subtomogram-microtubule",
        input_scale=1.0,
    )

    assert result.target_specimen == "Axonemal 13-Protofilament Microtubule with Kinesin-1 Dimers"
    assert result.confidence_score >= 0.95
    assert result.subtomogram_resolution_angstrom > 0.0
    assert result.motor_step_size_nm > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cryo-ET High-Densit" in result.summary_report
