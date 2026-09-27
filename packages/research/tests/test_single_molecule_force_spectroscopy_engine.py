"""Tests for Phase 239: Autonomous Single-Molecule Optical Tweezers & AFM Force-Induced Unfolding Kinetics Engine Engine."""

import pytest
from research.orchestration.single_molecule_force_spectroscopy_engine import SingleMoleculeForceSpectroscopyEngine


def test_single_molecule_force_spectroscopy_engine():
    engine = SingleMoleculeForceSpectroscopyEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-molecule-force-spectroscopy",
        input_scale=1.0,
    )
    assert getattr(result, "rupture_force_pico_newtons") != 0
    assert getattr(result, "transition_state_distance_angstrom") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
