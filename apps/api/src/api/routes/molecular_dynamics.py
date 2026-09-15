"""Autonomous Molecular Dynamics (MD) & Quantum Chemistry API Routes (Phase 39)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User as DBUser
from database.repositories.molecular_dynamics_repo import MolecularDynamicsRepository
from research.molecular_dynamics_engine import MolecularDynamicsEngine
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/md", tags=["molecular-dynamics"])
engine = MolecularDynamicsEngine()


# --- Pydantic Request / Response Schemas ---

class MDSimulateRequest(BaseModel):
    uniprot_id: str = Field(..., description="UniProt Accession ID (e.g. Q9BYF1, Q99250, P02766)")
    system_name: Optional[str] = Field(None, description="Descriptive system title (e.g. PCSK9_Evolocumab_Complex)")
    organism: str = Field("Homo sapiens", description="Host organism")
    forcefield: str = Field("AMBER14SB", description="AMBER14SB, CHARMM36m, OPLS_AA")
    solvent_model: str = Field("TIP3P", description="TIP3P, OPC, implicit_GB")
    ensemble: str = Field("NPT", description="NPT, NVT, NVE")
    total_duration_ns: float = Field(100.0, gt=0.0, le=1000.0, description="Simulation duration in nanoseconds")
    total_frames: int = Field(30, ge=5, le=100, description="Number of trajectory time-series frames")
    temperature_kelvin: float = Field(300.0, gt=0.0, description="Temperature in Kelvin")
    pressure_bar: float = Field(1.013, gt=0.0, description="Pressure in Bar")
    sequence: Optional[str] = Field(None, description="Custom FASTA amino acid sequence")
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


# --- Endpoint Implementations ---

@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_molecular_dynamics(
    payload: MDSimulateRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute all-atom molecular dynamics simulation, trajectory frames, RMSF flexibility, and quantum DFT analysis."""
    result = engine.simulate_trajectory(
        uniprot_id=payload.uniprot_id,
        system_name=payload.system_name,
        organism=payload.organism,
        forcefield=payload.forcefield,
        solvent_model=payload.solvent_model,
        ensemble=payload.ensemble,
        total_duration_ns=payload.total_duration_ns,
        total_frames=payload.total_frames,
        temperature_kelvin=payload.temperature_kelvin,
        pressure_bar=payload.pressure_bar,
        sequence=payload.sequence,
    )

    repo = MolecularDynamicsRepository(session)
    sim = await repo.create_simulation(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        uniprot_id=result.uniprot_id,
        system_name=result.system_name,
        organism=result.organism,
        forcefield=result.forcefield,
        solvent_model=result.solvent_model,
        ensemble=result.ensemble,
        total_frames=result.total_frames,
        timestep_ps=result.timestep_ps,
        total_duration_ns=result.total_duration_ns,
        temperature_kelvin=result.temperature_kelvin,
        pressure_bar=result.pressure_bar,
        equilibrium_rmsd_angstrom=result.equilibrium_rmsd_angstrom,
        thermodynamic_data_json=result.thermodynamic_data_json,
    )

    # Persist Trajectory Frames
    frames = await repo.add_trajectory_frames(
        simulation_id=sim.id,
        frames_data=[f.model_dump() for f in result.trajectory_frames],
    )

    # Persist Residue Fluctuations
    fluctuations = await repo.add_residue_fluctuations(
        simulation_id=sim.id,
        fluctuations_data=[r.model_dump() for r in result.residue_fluctuations],
    )

    # Persist Quantum DFT Properties
    q = result.quantum_properties
    quantum_prop = await repo.set_quantum_properties(
        simulation_id=sim.id,
        dft_method=q.dft_method,
        homo_energy_ev=q.homo_energy_ev,
        lumo_energy_ev=q.lumo_energy_ev,
        bandgap_energy_ev=q.bandgap_energy_ev,
        dipole_moment_debye=q.dipole_moment_debye,
        polarizability_angstrom3=q.polarizability_angstrom3,
        total_scf_energy_hartree=q.total_scf_energy_hartree,
        mulliken_partial_charges_json=q.mulliken_partial_charges_json,
        electrostatic_potential_surface_json=q.electrostatic_potential_surface_json,
    )

    await session.commit()
    logger.info("md_simulation_persisted", simulation_id=str(sim.id), uniprot=sim.uniprot_id, frames=len(frames))

    return {
        "id": str(sim.id),
        "uniprot_id": sim.uniprot_id,
        "system_name": sim.system_name,
        "organism": sim.organism,
        "forcefield": sim.forcefield,
        "solvent_model": sim.solvent_model,
        "ensemble": sim.ensemble,
        "total_frames": sim.total_frames,
        "timestep_ps": sim.timestep_ps,
        "total_duration_ns": sim.total_duration_ns,
        "temperature_kelvin": sim.temperature_kelvin,
        "pressure_bar": sim.pressure_bar,
        "equilibrium_rmsd_angstrom": sim.equilibrium_rmsd_angstrom,
        "thermodynamic_data": sim.thermodynamic_data_json,
        "quantum_properties": {
            "dft_method": quantum_prop.dft_method,
            "homo_energy_ev": quantum_prop.homo_energy_ev,
            "lumo_energy_ev": quantum_prop.lumo_energy_ev,
            "bandgap_energy_ev": quantum_prop.bandgap_energy_ev,
            "dipole_moment_debye": quantum_prop.dipole_moment_debye,
            "polarizability_angstrom3": quantum_prop.polarizability_angstrom3,
            "total_scf_energy_hartree": quantum_prop.total_scf_energy_hartree,
            "mulliken_partial_charges": quantum_prop.mulliken_partial_charges_json,
            "electrostatic_surface": quantum_prop.electrostatic_potential_surface_json,
        },
        "frames_count": len(frames),
        "residue_fluctuations_count": len(fluctuations),
        "created_at": sim.created_at.isoformat(),
    }


@router.get("/simulations")
async def list_simulations(
    uniprot_id: Optional[str] = Query(None, description="Filter by UniProt ID"),
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List molecular dynamics simulations with summary metrics."""
    repo = MolecularDynamicsRepository(session)
    sims = await repo.list_simulations(
        user_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        uniprot_id=uniprot_id,
        limit=limit,
        offset=offset,
    )

    return [
        {
            "id": str(s.id),
            "uniprot_id": s.uniprot_id,
            "system_name": s.system_name,
            "organism": s.organism,
            "forcefield": s.forcefield,
            "solvent_model": s.solvent_model,
            "total_duration_ns": s.total_duration_ns,
            "total_frames": s.total_frames,
            "equilibrium_rmsd_angstrom": s.equilibrium_rmsd_angstrom,
            "bandgap_energy_ev": s.quantum_properties.bandgap_energy_ev if s.quantum_properties else 4.24,
            "created_at": s.created_at.isoformat(),
        }
        for s in sims
    ]


@router.get("/simulations/{simulation_id}")
async def get_simulation(
    simulation_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve detailed simulation data with time-series frames, RMSF fluctuations, and quantum DFT analysis."""
    repo = MolecularDynamicsRepository(session)
    sim = await repo.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Molecular dynamics simulation '{simulation_id}' not found.",
        )

    return {
        "id": str(sim.id),
        "uniprot_id": sim.uniprot_id,
        "system_name": sim.system_name,
        "organism": sim.organism,
        "forcefield": sim.forcefield,
        "solvent_model": sim.solvent_model,
        "ensemble": sim.ensemble,
        "total_frames": sim.total_frames,
        "timestep_ps": sim.timestep_ps,
        "total_duration_ns": sim.total_duration_ns,
        "temperature_kelvin": sim.temperature_kelvin,
        "pressure_bar": sim.pressure_bar,
        "equilibrium_rmsd_angstrom": sim.equilibrium_rmsd_angstrom,
        "thermodynamic_data": sim.thermodynamic_data_json,
        "quantum_properties": {
            "dft_method": sim.quantum_properties.dft_method,
            "homo_energy_ev": sim.quantum_properties.homo_energy_ev,
            "lumo_energy_ev": sim.quantum_properties.lumo_energy_ev,
            "bandgap_energy_ev": sim.quantum_properties.bandgap_energy_ev,
            "dipole_moment_debye": sim.quantum_properties.dipole_moment_debye,
            "polarizability_angstrom3": sim.quantum_properties.polarizability_angstrom3,
            "total_scf_energy_hartree": sim.quantum_properties.total_scf_energy_hartree,
            "mulliken_partial_charges": sim.quantum_properties.mulliken_partial_charges_json,
            "electrostatic_surface": sim.quantum_properties.electrostatic_potential_surface_json,
        } if sim.quantum_properties else None,
        "trajectory_frames": [
            {
                "id": str(f.id),
                "frame_index": f.frame_index,
                "timestamp_ps": f.timestamp_ps,
                "rmsd_angstrom": f.rmsd_angstrom,
                "radius_of_gyration_angstrom": f.radius_of_gyration_angstrom,
                "potential_energy_kj_mol": f.potential_energy_kj_mol,
                "kinetic_energy_kj_mol": f.kinetic_energy_kj_mol,
                "total_energy_kj_mol": f.total_energy_kj_mol,
                "temperature_kelvin": f.temperature_kelvin,
            }
            for f in sim.trajectory_frames
        ],
        "residue_fluctuations": [
            {
                "id": str(r.id),
                "residue_number": r.residue_number,
                "residue_name": r.residue_name,
                "rmsf_angstrom": r.rmsf_angstrom,
                "b_factor_equivalent": r.b_factor_equivalent,
                "is_flexible_loop": r.is_flexible_loop,
                "secondary_structure_type": r.secondary_structure_type,
            }
            for r in sim.residue_fluctuations
        ],
        "created_at": sim.created_at.isoformat(),
    }


@router.get("/simulations/{simulation_id}/frames/{frame_index}")
async def get_trajectory_frame(
    simulation_id: uuid.UUID,
    frame_index: int,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch individual coordinate frame for interactive 3D playback."""
    repo = MolecularDynamicsRepository(session)
    sim = await repo.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation '{simulation_id}' not found.",
        )

    frame = next((f for f in sim.trajectory_frames if f.frame_index == frame_index), None)
    if not frame:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Frame '{frame_index}' not found in simulation.",
        )

    return {
        "simulation_id": str(sim.id),
        "frame_index": frame.frame_index,
        "timestamp_ps": frame.timestamp_ps,
        "rmsd_angstrom": frame.rmsd_angstrom,
        "pdb_coordinates": frame.frame_pdb_coordinates,
        "potential_energy_kj_mol": frame.potential_energy_kj_mol,
        "temperature_kelvin": frame.temperature_kelvin,
    }


@router.get("/simulations/{simulation_id}/export-trajectory")
async def export_trajectory_pdb(
    simulation_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Download concatenated multi-frame PDB trajectory stream."""
    repo = MolecularDynamicsRepository(session)
    sim = await repo.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation '{simulation_id}' not found.",
        )

    stream_blocks = []
    stream_blocks.append(f"HEADER    MD MULTI-MODEL TRAJECTORY {sim.uniprot_id}\n")
    for f in sim.trajectory_frames:
        stream_blocks.append(f"MODEL     {f.frame_index}\n")
        stream_blocks.append(f.frame_pdb_coordinates.strip() + "\n")
        stream_blocks.append("ENDMDL\n")

    return Response(
        content="".join(stream_blocks),
        media_type="chemical/x-pdb",
        headers={"Content-Disposition": f'attachment; filename="{sim.system_name}_trajectory.pdb"'},
    )
