"""Tests for Phase 290: Autonomous Intact Membrane Protein Native Mass Spectrometry & Lipid-Binding Stoichiometry Engine Engine."""

import pytest
from research.orchestration.native_mass_spec_membrane_protein_engine import NativeMassSpecMembraneProteinEngine


def test_native_mass_spec_membrane_protein_engine():
    engine = NativeMassSpecMembraneProteinEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="native-mass-spec-membrane-protein",
        input_scale=1.0,
    )
    assert getattr(result, "oligomeric_stoichiometry_confidence_score") != 0
    assert getattr(result, "lipid_dissociation_constant_kd_uM") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
