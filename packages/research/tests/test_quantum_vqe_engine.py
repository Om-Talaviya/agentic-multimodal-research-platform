"""Tests for QuantumChemistryVQEEngine."""
import pytest
from research.quantum.quantum_vqe_engine import QuantumChemistryVQEEngine


def test_quantum_vqe_simulation_h2():
    engine = QuantumChemistryVQEEngine()
    result = engine.run_vqe_simulation(
        molecule_key="H2",
        ansatz_type="UCCSD",
        optimizer="COBYLA",
        max_iterations=30,
    )

    assert "system" in result
    assert result["system"]["num_qubits"] == 4
    assert result["system"]["active_electrons"] == 2

    assert "vqe_execution" in result
    vqe = result["vqe_execution"]
    assert vqe["ansatz_type"] == "UCCSD"
    assert len(vqe["convergence_curve"]) == 30
    assert vqe["ground_state_energy_hartree"] < 0
    assert vqe["energy_error_kcal_mol"] <= 1.0  # chemical accuracy
    assert vqe["chemical_accuracy_reached"] is True

    assert "energy_states" in result
    assert len(result["energy_states"]) >= 2
    assert result["energy_states"][0]["is_ground_state"] is True


def test_quantum_vqe_simulation_lih():
    engine = QuantumChemistryVQEEngine()
    result = engine.run_vqe_simulation(
        molecule_key="LiH",
        ansatz_type="HEA",
        optimizer="SPSA",
        max_iterations=20,
    )

    assert result["system"]["num_qubits"] == 6
    assert result["vqe_execution"]["ansatz_type"] == "HEA"
    assert result["vqe_execution"]["ground_state_energy_hartree"] < -7.0
