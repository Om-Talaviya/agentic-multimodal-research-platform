"""Tests for QuantumChemistryRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.quantum_chemistry_repo import QuantumChemistryRepository


@pytest.mark.asyncio
async def test_quantum_chemistry_repo_lifecycle(db_session: AsyncSession):
    repo = QuantumChemistryRepository(db_session)

    # 1. Create System
    system = await repo.create_system(
        molecule_name="Molecular Hydrogen (H2)",
        smiles_formula="[H][H]",
        basis_set="STO-3G",
        charge=0,
        multiplicity=1,
        num_qubits=4,
        active_electrons=2,
        active_orbitals=2,
        nuclear_repulsion_energy=0.71375,
    )
    assert system.id is not None
    assert system.molecule_name == "Molecular Hydrogen (H2)"
    assert system.num_qubits == 4

    # 2. Add VQE Execution
    execution = await repo.add_vqe_execution(
        system_id=system.id,
        ansatz_type="UCCSD",
        optimizer_algorithm="COBYLA",
        ground_state_energy_hartree=-1.13728,
        exact_fci_energy_hartree=-1.13730,
        energy_error_kcal_mol=0.0125,
        chemical_accuracy_reached=True,
        iteration_count=35,
        execution_time_seconds=0.85,
        optimal_parameters_json=[0.12, -0.45],
    )
    assert execution.id is not None
    assert execution.chemical_accuracy_reached is True

    # 3. Add Energy States
    state = await repo.add_energy_state(
        system_id=system.id,
        state_label="Ground State (S0)",
        expectation_energy=-1.13728,
        dipole_moment_debye=0.0,
        spin_multiplicity=1,
        is_ground_state=True,
    )
    assert state.id is not None
    assert state.is_ground_state is True

    # 4. Query System
    fetched = await repo.get_system(system.id)
    assert fetched is not None
    assert len(fetched.ansatz_executions) == 1
    assert len(fetched.energy_states) == 1

    # 5. List Systems
    systems = await repo.list_systems()
    assert len(systems) >= 1
