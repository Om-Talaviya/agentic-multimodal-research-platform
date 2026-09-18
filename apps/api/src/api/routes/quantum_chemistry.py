"""API Routes for Quantum Chemistry & Molecular Hamiltonian VQE Simulation."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.quantum_chemistry_repo import QuantumChemistryRepository
from research.quantum.quantum_vqe_engine import QuantumChemistryVQEEngine

router = APIRouter(prefix="/quantum-chemistry", tags=["Quantum Chemistry & VQE Simulation"])


class VQESimulateRequest(BaseModel):
    molecule_key: str = Field(default="H2", description="Molecule key: H2, LiH, BeH2, H2O")
    ansatz_type: str = Field(default="UCCSD", description="Ansatz type: UCCSD, HEA, RY")
    optimizer: str = Field(default="COBYLA", description="Classical optimizer: COBYLA, SPSA, ADAM")
    max_iterations: int = Field(default=40, ge=5, le=200)


@router.get("/molecules")
async def get_supported_molecules():
    """List preset molecules available for quantum chemical simulation."""
    return {"molecules": QuantumChemistryVQEEngine.MOLECULE_DATABASE}


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def run_quantum_simulation(
    request: VQESimulateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Execute VQE simulation and persist results."""
    engine = QuantumChemistryVQEEngine()
    sim_result = engine.run_vqe_simulation(
        molecule_key=request.molecule_key,
        ansatz_type=request.ansatz_type,
        optimizer=request.optimizer,
        max_iterations=request.max_iterations,
    )

    repo = QuantumChemistryRepository(db)
    sys_info = sim_result["system"]
    system = await repo.create_system(
        molecule_name=sys_info["molecule_name"],
        smiles_formula=sys_info["smiles_formula"],
        basis_set=sys_info["basis_set"],
        num_qubits=sys_info["num_qubits"],
        active_electrons=sys_info["active_electrons"],
        active_orbitals=sys_info["active_orbitals"],
        nuclear_repulsion_energy=sys_info["nuclear_repulsion_energy"],
        geometry_json={"exact_fci_energy": sys_info["exact_fci_energy_hartree"]},
    )

    vqe_info = sim_result["vqe_execution"]
    execution = await repo.add_vqe_execution(
        system_id=system.id,
        ansatz_type=vqe_info["ansatz_type"],
        optimizer_algorithm=vqe_info["optimizer_algorithm"],
        ground_state_energy_hartree=vqe_info["ground_state_energy_hartree"],
        exact_fci_energy_hartree=vqe_info["exact_fci_energy_hartree"],
        energy_error_kcal_mol=vqe_info["energy_error_kcal_mol"],
        chemical_accuracy_reached=vqe_info["chemical_accuracy_reached"],
        iteration_count=vqe_info["iteration_count"],
        execution_time_seconds=vqe_info["execution_time_seconds"],
        optimal_parameters_json=vqe_info["optimal_parameters"],
    )

    for state in sim_result["energy_states"]:
        await repo.add_energy_state(
            system_id=system.id,
            state_label=state["state_label"],
            expectation_energy=state["expectation_energy"],
            dipole_moment_debye=state["dipole_moment_debye"],
            spin_multiplicity=state["spin_multiplicity"],
            is_ground_state=state["is_ground_state"],
        )

    saved_system = await repo.get_system(system.id)
    return {
        "status": "success",
        "system_id": system.id,
        "molecule": sys_info["molecule_name"],
        "ground_state_energy_hartree": vqe_info["ground_state_energy_hartree"],
        "chemical_accuracy_reached": vqe_info["chemical_accuracy_reached"],
        "energy_error_kcal_mol": vqe_info["energy_error_kcal_mol"],
        "convergence_curve": vqe_info["convergence_curve"],
        "energy_states_count": len(saved_system.energy_states if saved_system else []),
    }


@router.get("/systems")
async def list_quantum_systems(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent quantum molecular systems and simulations."""
    repo = QuantumChemistryRepository(db)
    systems = await repo.list_systems(limit=limit)
    return [
        {
            "id": s.id,
            "molecule_name": s.molecule_name,
            "smiles_formula": s.smiles_formula,
            "num_qubits": s.num_qubits,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "ansatz_executions_count": len(s.ansatz_executions),
            "energy_states_count": len(s.energy_states),
        }
        for s in systems
    ]


@router.get("/systems/{system_id}")
async def get_quantum_system(
    system_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve detailed quantum simulation data for a system."""
    repo = QuantumChemistryRepository(db)
    system = await repo.get_system(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="Quantum system not found")

    return {
        "id": system.id,
        "molecule_name": system.molecule_name,
        "smiles_formula": system.smiles_formula,
        "basis_set": system.basis_set,
        "num_qubits": system.num_qubits,
        "active_electrons": system.active_electrons,
        "active_orbitals": system.active_orbitals,
        "nuclear_repulsion_energy": system.nuclear_repulsion_energy,
        "ansatz_executions": [
            {
                "id": ex.id,
                "ansatz_type": ex.ansatz_type,
                "optimizer_algorithm": ex.optimizer_algorithm,
                "ground_state_energy_hartree": ex.ground_state_energy_hartree,
                "exact_fci_energy_hartree": ex.exact_fci_energy_hartree,
                "energy_error_kcal_mol": ex.energy_error_kcal_mol,
                "chemical_accuracy_reached": ex.chemical_accuracy_reached,
                "iteration_count": ex.iteration_count,
            }
            for ex in system.ansatz_executions
        ],
        "energy_states": [
            {
                "id": st.id,
                "state_label": st.state_label,
                "expectation_energy": st.expectation_energy,
                "dipole_moment_debye": st.dipole_moment_debye,
                "spin_multiplicity": st.spin_multiplicity,
                "is_ground_state": st.is_ground_state,
            }
            for st in system.energy_states
        ],
    }
