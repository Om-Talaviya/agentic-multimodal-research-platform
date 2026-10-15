"""Tests for Phase 537: Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

import pytest
from research.orchestration.single_molecule_magnetic_torque_tweezer_engine import SingleMoleculeMagneticTorqueTweezerEngine


def test_single_molecule_magnetic_torque_tweezer_engine():
    engine = SingleMoleculeMagneticTorqueTweezerEngine()
    result = engine.analyze(
        target_specimen="Tethered 10-kb Double-Stranded DNA Molecule with Cylindrical Magnetic Bead in Horizontal Torque Field",
        analytical_modality="magnetic-torque-tweezers-supercoiling",
        input_scale=1.0,
    )

    assert result.target_specimen == "Tethered 10-kb Double-Stranded DNA Molecule with Cylindrical Magnetic Bead in Horizontal Torque Field"
    assert result.confidence_score >= 0.95
    assert result.torsional_persistence_length_nm != 0.0
    assert result.buckling_transition_critical_torque_pN_nm != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Molecule Mag" in result.summary_report
