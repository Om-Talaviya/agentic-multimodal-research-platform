"""Tests for Phase 549: Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

import pytest
from research.orchestration.active_chiral_hydrodynamics_vorticity_engine import ActiveChiralHydrodynamicsVorticityEngine


def test_active_chiral_hydrodynamics_vorticity_engine():
    engine = ActiveChiralHydrodynamicsVorticityEngine()
    result = engine.analyze(
        target_specimen="Chiral Rotating Flagellated Micro-Swarm Escherichia coli in Confined Annular Microfluidic Cavities",
        analytical_modality="active-chiral-hydrodynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Chiral Rotating Flagellated Micro-Swarm Escherichia coli in Confined Annular Microfluidic Cavities"
    assert result.confidence_score >= 0.95
    assert result.swarming_vorticity_enstrophy_density_s2 != 0.0
    assert result.chiral_odd_viscosity_coefficient_pa_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Non-Equilibrium Act" in result.summary_report
