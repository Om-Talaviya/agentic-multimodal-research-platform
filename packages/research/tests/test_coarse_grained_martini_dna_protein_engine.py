"""Tests for Phase 447: Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

import pytest
from research.orchestration.coarse_grained_martini_dna_protein_engine import CoarseGrainedMartiniDnaProteinEngine


def test_coarse_grained_martini_dna_protein_engine():
    engine = CoarseGrainedMartiniDnaProteinEngine()
    result = engine.analyze(
        target_specimen="Nucleosome Core Particle Octamer with 147bp Wrapped DNA in 150mM Salt Solvation Box",
        analytical_modality="coarse-grained-martini-dynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Nucleosome Core Particle Octamer with 147bp Wrapped DNA in 150mM Salt Solvation Box"
    assert result.confidence_score >= 0.95
    assert result.bead_rmsd_convergence_angstrom != 0.0
    assert result.electrostatic_solvation_free_energy_kcal_mol != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Coarse-Grained DNA-" in result.summary_report
