"""Tests for Cryo-ET Subtomogram Averaging Engine."""

import pytest
from research.structural.cryoet_subtomogram_tomography_engine import CryoETTomogramEngine


def test_cryoet_tomogram_engine_reconstruction() -> None:
    engine = CryoETTomogramEngine()
    result = engine.run_subtomogram_averaging(
        study_name="AMPAR-TARP Cryo-ET Study",
        cellular_context="Intact Neuronal Synapse (In-Situ)",
        target_complex_name="AMPAR-TARP Ion Channel Complex",
    )

    assert result["study_name"] == "AMPAR-TARP Cryo-ET Study"
    assert result["particles_picked_count"] == 4
    assert result["final_fsc_resolution_angstrom"] < 4.0
    assert len(result["particles"]) == 4
    assert len(result["classes"]) >= 3

    # Check particle properties
    first_ptcl = result["particles"][0]
    assert "particle_id_str" in first_ptcl
    assert "cross_correlation_score" in first_ptcl
    assert "conformational_state" in first_ptcl
