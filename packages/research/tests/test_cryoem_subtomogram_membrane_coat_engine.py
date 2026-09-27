"""Tests for Phase 226: Autonomous In-Situ Cryo-ET Membrane Coat & Clathrin/COP-II Lattice Structural Fitting Engine Engine."""

import pytest
from research.orchestration.cryoem_subtomogram_membrane_coat_engine import CryoEMSubtomogramMembraneCoatEngine


def test_cryoem_subtomogram_membrane_coat_engine():
    engine = CryoEMSubtomogramMembraneCoatEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-subtomogram-membrane-coat",
        input_scale=1.0,
    )
    assert getattr(result, "subtomogram_fsc_resolution_angstrom") != 0
    assert getattr(result, "lattice_curvature_radius_nm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
