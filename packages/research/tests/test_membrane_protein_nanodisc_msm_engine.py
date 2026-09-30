"""Tests for Phase 396: Membrane Protein Lipid Nanodisc Molecular Dynamics Markov State Modeler Engine."""

import pytest
from research.orchestration.membrane_protein_nanodisc_msm_engine import MembraneProteinNanodiscMsmEngine


def test_membrane_protein_nanodisc_msm_engine():
    engine = MembraneProteinNanodiscMsmEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="membrane-protein-nanodisc-msm",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "conformation_free_energy_barrier_kcal_mol") > 0
    assert getattr(result, "markov_state_transition_rate_per_microsec") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 396" in result.summary_report
