"""Tests for Phase 575: Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

import pytest
from research.orchestration.cryo_et_subtomogram_membrane_coat_assembler_engine import CryoEtSubtomogramMembraneCoatAssemblerEngine


def test_cryo_et_subtomogram_membrane_coat_assembler_engine():
    engine = CryoEtSubtomogramMembraneCoatAssemblerEngine()
    result = engine.analyze(
        target_specimen="Vitrified Saccharomyces cerevisiae Budding Vesicle Donor Sites with COP-II Polyhedral Lattice Outer Shell",
        analytical_modality="cryoet-subtomogram-coat-assembly",
        input_scale=1.0,
    )
    assert result is not None
    assert result.subtomogram_resolution_fsc0143_a != 0.0
    assert result.cage_polyhedral_symmetry_index != 0.0
    assert result.membrane_curvature_coupling_energy_kbt != 0.0
    assert result.angular_orientation_precision_deg != 0.0
    assert result.confidence_score >= 0.90
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert result.target_specimen == "Vitrified Saccharomyces cerevisiae Budding Vesicle Donor Sites with COP-II Polyhedral Lattice Outer Shell"
    assert result.analytical_modality == "cryoet-subtomogram-coat-assembly"
