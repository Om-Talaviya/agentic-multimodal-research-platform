"""Tests for AlphaFold Complex Docking Engine."""

import pytest
from research.structural.alphafold_complex_docking_engine import AlphaFoldComplexDockingEngine


def test_alphafold_complex_docking_engine_prediction() -> None:
    engine = AlphaFoldComplexDockingEngine()
    result = engine.predict_complex_docking(
        study_name="PD-1 / PD-L1 Complex Docking",
        target_complex_name="PD-1 / PD-L1 Complex",
    )

    assert result["study_name"] == "PD-1 / PD-L1 Complex Docking"
    assert result["mean_iptm_score"] >= 0.70
    assert result["mean_plddt_interface"] > 70.0
    assert result["buried_surface_area_angstrom2"] > 1000.0
    assert len(result["contacts"]) >= 4
    assert len(result["energy_metrics"]) >= 5

    # Check contact properties
    first_contact = result["contacts"][0]
    assert "chain_a_residue" in first_contact
    assert "chain_b_residue" in first_contact
    assert "predicted_aligned_error_angstrom" in first_contact
    assert "inter_residue_distance_angstrom" in first_contact
