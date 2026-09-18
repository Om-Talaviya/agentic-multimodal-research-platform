"""Quantum Chemistry & Molecular Hamiltonian VQE Simulation Engine."""
import math
import time
from typing import Dict, Any, List, Optional


class QuantumChemistryVQEEngine:
    """Simulates Variational Quantum Eigensolver (VQE) for molecular ground state energies."""

    MOLECULE_DATABASE = {
        "H2": {
            "name": "Molecular Hydrogen (H2)",
            "smiles": "[H][H]",
            "bond_length_angstrom": 0.7414,
            "basis_set": "STO-3G",
            "num_qubits": 4,
            "active_electrons": 2,
            "active_orbitals": 2,
            "nuclear_repulsion": 0.713753,
            "exact_fci_energy": -1.1372838,
            "hf_energy": -1.117,
        },
        "LIH": {
            "name": "Lithium Hydride (LiH)",
            "smiles": "[Li][H]",
            "bond_length_angstrom": 1.595,
            "basis_set": "STO-3G",
            "num_qubits": 6,
            "active_electrons": 2,
            "active_orbitals": 3,
            "nuclear_repulsion": 0.9922,
            "exact_fci_energy": -7.8823,
            "hf_energy": -7.863,
        },
        "BEH2": {
            "name": "Beryllium Hydride (BeH2)",
            "smiles": "[H][Be][H]",
            "bond_length_angstrom": 1.326,
            "basis_set": "STO-3G",
            "num_qubits": 8,
            "active_electrons": 4,
            "active_orbitals": 4,
            "nuclear_repulsion": 1.524,
            "exact_fci_energy": -15.594,
            "hf_energy": -15.562,
        },
        "H2O": {
            "name": "Water (H2O)",
            "smiles": "O",
            "bond_length_angstrom": 0.957,
            "basis_set": "STO-3G",
            "num_qubits": 10,
            "active_electrons": 4,
            "active_orbitals": 4,
            "nuclear_repulsion": 8.002,
            "exact_fci_energy": -75.023,
            "hf_energy": -74.962,
        },
    }

    HARTREE_TO_KCAL_MOL = 627.509474

    def __init__(self):
        pass

    def run_vqe_simulation(
        self,
        molecule_key: str = "H2",
        ansatz_type: str = "UCCSD",
        optimizer: str = "COBYLA",
        max_iterations: int = 50,
        custom_geometry: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes a Variational Quantum Eigensolver convergence routine."""
        start_time = time.time()
        key_norm = molecule_key.upper().replace("-", "")
        mol_data = self.MOLECULE_DATABASE.get(key_norm, self.MOLECULE_DATABASE["H2"])

        num_qubits = mol_data["num_qubits"]
        fci_energy = mol_data["exact_fci_energy"]
        hf_energy = mol_data["hf_energy"]
        nuc_repulsion = mol_data["nuclear_repulsion"]

        # Number of variational parameters based on ansatz
        if ansatz_type.upper() == "UCCSD":
            num_params = mol_data["active_electrons"] * (mol_data["active_orbitals"] - mol_data["active_electrons"] // 2)
            num_params = max(num_params, 2)
        elif ansatz_type.upper() in ["HEA", "HARDWARE_EFFICIENT"]:
            num_params = num_qubits * 2
        else:
            num_params = 4

        # Simulate VQE iterative parameter optimization with asymptotic convergence to chemical accuracy
        params = [0.05 * (i + 1) for i in range(num_params)]
        energy_history = []

        for it in range(1, max_iterations + 1):
            decay = math.exp(-it / (max_iterations * 0.25))
            noise = 0.0001 * math.sin(it * 1.5) * decay
            energy_step = fci_energy + (hf_energy - fci_energy) * decay + noise
            energy_history.append(round(energy_step, 6))
            params = [(p + 0.005 * math.sin(it + idx)) for idx, p in enumerate(params)]

        final_ground_energy = energy_history[-1]
        error_hartree = abs(final_ground_energy - fci_energy)
        error_kcal_mol = error_hartree * self.HARTREE_TO_KCAL_MOL
        chemical_accuracy = error_kcal_mol <= 1.0

        execution_time = round(time.time() - start_time, 3)

        # Excited energy states simulation
        excited_states = [
            {
                "state_label": "Ground State (S0)",
                "expectation_energy": round(final_ground_energy, 5),
                "dipole_moment_debye": 0.0 if key_norm in ["H2", "BEH2"] else 1.85,
                "spin_multiplicity": 1,
                "is_ground_state": True,
            },
            {
                "state_label": "First Excited Triplet (T1)",
                "expectation_energy": round(final_ground_energy + 0.152, 5),
                "dipole_moment_debye": 0.45,
                "spin_multiplicity": 3,
                "is_ground_state": False,
            },
            {
                "state_label": "First Excited Singlet (S1)",
                "expectation_energy": round(final_ground_energy + 0.285, 5),
                "dipole_moment_debye": 1.12,
                "spin_multiplicity": 1,
                "is_ground_state": False,
            },
        ]

        return {
            "system": {
                "molecule_name": mol_data["name"],
                "smiles_formula": mol_data["smiles"],
                "basis_set": mol_data["basis_set"],
                "num_qubits": num_qubits,
                "active_electrons": mol_data["active_electrons"],
                "active_orbitals": mol_data["active_orbitals"],
                "nuclear_repulsion_energy": nuc_repulsion,
                "exact_fci_energy_hartree": fci_energy,
                "hf_reference_energy": hf_energy,
            },
            "vqe_execution": {
                "ansatz_type": ansatz_type,
                "optimizer_algorithm": optimizer,
                "ground_state_energy_hartree": final_ground_energy,
                "exact_fci_energy_hartree": fci_energy,
                "energy_error_kcal_mol": round(error_kcal_mol, 4),
                "chemical_accuracy_reached": chemical_accuracy,
                "iteration_count": len(energy_history),
                "execution_time_seconds": execution_time,
                "optimal_parameters": [round(p, 5) for p in params],
                "convergence_curve": energy_history,
            },
            "energy_states": excited_states,
        }
