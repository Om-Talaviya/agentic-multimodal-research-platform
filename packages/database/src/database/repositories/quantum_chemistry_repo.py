"""Repository for Quantum Chemistry & VQE Molecular Simulation."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.quantum_chemistry import (
    DBQuantumMolecularSystem,
    DBVQEAnsatzExecution,
    DBHamiltonianEnergyState,
)


class QuantumChemistryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_system(
        self,
        molecule_name: str,
        smiles_formula: str = "H2",
        basis_set: str = "STO-3G",
        charge: int = 0,
        multiplicity: int = 1,
        num_qubits: int = 4,
        active_electrons: int = 2,
        active_orbitals: int = 2,
        nuclear_repulsion_energy: float = 0.71375,
        geometry_json: Optional[Dict[str, Any]] = None,
    ) -> DBQuantumMolecularSystem:
        system = DBQuantumMolecularSystem(
            molecule_name=molecule_name,
            smiles_formula=smiles_formula,
            basis_set=basis_set,
            charge=charge,
            multiplicity=multiplicity,
            num_qubits=num_qubits,
            active_electrons=active_electrons,
            active_orbitals=active_orbitals,
            nuclear_repulsion_energy=nuclear_repulsion_energy,
            geometry_json=geometry_json or {},
        )
        self.session.add(system)
        await self.session.commit()
        await self.session.refresh(system)
        return system

    async def add_vqe_execution(
        self,
        system_id: str,
        ansatz_type: str = "UCCSD",
        optimizer_algorithm: str = "COBYLA",
        ground_state_energy_hartree: float = -1.137,
        exact_fci_energy_hartree: float = -1.1373,
        energy_error_kcal_mol: float = 0.188,
        chemical_accuracy_reached: bool = True,
        iteration_count: int = 42,
        execution_time_seconds: float = 1.25,
        optimal_parameters_json: Optional[List[float]] = None,
    ) -> DBVQEAnsatzExecution:
        execution = DBVQEAnsatzExecution(
            system_id=system_id,
            ansatz_type=ansatz_type,
            optimizer_algorithm=optimizer_algorithm,
            ground_state_energy_hartree=ground_state_energy_hartree,
            exact_fci_energy_hartree=exact_fci_energy_hartree,
            energy_error_kcal_mol=energy_error_kcal_mol,
            chemical_accuracy_reached=chemical_accuracy_reached,
            iteration_count=iteration_count,
            execution_time_seconds=execution_time_seconds,
            optimal_parameters_json=optimal_parameters_json or [],
        )
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def add_energy_state(
        self,
        system_id: str,
        state_label: str = "Ground State (S0)",
        expectation_energy: float = -1.137,
        dipole_moment_debye: float = 0.0,
        spin_multiplicity: int = 1,
        is_ground_state: bool = True,
    ) -> DBHamiltonianEnergyState:
        state = DBHamiltonianEnergyState(
            system_id=system_id,
            state_label=state_label,
            expectation_energy=expectation_energy,
            dipole_moment_debye=dipole_moment_debye,
            spin_multiplicity=spin_multiplicity,
            is_ground_state=is_ground_state,
        )
        self.session.add(state)
        await self.session.commit()
        await self.session.refresh(state)
        return state

    async def get_system(self, system_id: str) -> Optional[DBQuantumMolecularSystem]:
        stmt = (
            select(DBQuantumMolecularSystem)
            .where(DBQuantumMolecularSystem.id == system_id)
            .options(
                selectinload(DBQuantumMolecularSystem.ansatz_executions),
                selectinload(DBQuantumMolecularSystem.energy_states),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_systems(self, limit: int = 50) -> List[DBQuantumMolecularSystem]:
        stmt = (
            select(DBQuantumMolecularSystem)
            .options(
                selectinload(DBQuantumMolecularSystem.ansatz_executions),
                selectinload(DBQuantumMolecularSystem.energy_states),
            )
            .order_by(desc(DBQuantumMolecularSystem.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
