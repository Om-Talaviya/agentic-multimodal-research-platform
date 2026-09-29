"""Tests for Phase 330: Autonomous Quantum-Accelerated Molecular Orbital Active Space CASSCF/DMRG Solver Engine."""

import pytest
from research.orchestration.quantum_orbital_dmrg_engine import QuantumOrbitalDmrgEngine


def test_quantum_orbital_dmrg_engine():
    engine = QuantumOrbitalDmrgEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="quantum-orbital-dmrg",
        input_scale=1.0,
    )
    assert getattr(result, "dmrg_active_space_energy_hartree") != 0
    assert getattr(result, "von_neumann_orbital_entanglement_entropy") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
