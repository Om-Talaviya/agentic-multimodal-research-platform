"""Autonomous Molecular Dynamics & Quantum Chemistry Repository (Phase 39)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.molecular_dynamics import (
    DBMolecularDynamicsSimulation,
    DBQuantumChemistryProperty,
    DBResidueFluctuation,
    DBTrajectoryFrame,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class MolecularDynamicsRepository:
    """Async repository for Molecular Dynamics simulations, trajectory frames, RMSF curves, and quantum DFT properties."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_simulation(
        self,
        user_id: uuid.UUID | str,
        uniprot_id: str,
        system_name: str,
        organism: str = "Homo sapiens",
        forcefield: str = "AMBER14SB",
        solvent_model: str = "TIP3P",
        ensemble: str = "NPT",
        total_frames: int = 50,
        timestep_ps: float = 2.0,
        total_duration_ns: float = 100.0,
        temperature_kelvin: float = 300.0,
        pressure_bar: float = 1.013,
        equilibrium_rmsd_angstrom: float = 1.42,
        thermodynamic_data_json: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
    ) -> DBMolecularDynamicsSimulation:
        """Create and persist a new molecular dynamics simulation record."""
        sim = DBMolecularDynamicsSimulation(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            uniprot_id=uniprot_id.upper(),
            system_name=system_name,
            organism=organism,
            forcefield=forcefield,
            solvent_model=solvent_model,
            ensemble=ensemble,
            total_frames=total_frames,
            timestep_ps=timestep_ps,
            total_duration_ns=total_duration_ns,
            temperature_kelvin=temperature_kelvin,
            pressure_bar=pressure_bar,
            equilibrium_rmsd_angstrom=equilibrium_rmsd_angstrom,
            thermodynamic_data_json=thermodynamic_data_json or {},
            status="completed",
        )
        self._session.add(sim)
        await self._session.flush()
        logger.info(
            "md_simulation_created",
            simulation_id=str(sim.id),
            uniprot_id=uniprot_id,
            system_name=system_name,
            duration_ns=total_duration_ns,
        )
        return sim

    async def get_simulation(self, simulation_id: uuid.UUID | str) -> Optional[DBMolecularDynamicsSimulation]:
        """Fetch a simulation by ID with all trajectory frames, RMSF fluctuations, and quantum properties."""
        stmt = (
            select(DBMolecularDynamicsSimulation)
            .where(DBMolecularDynamicsSimulation.id == simulation_id)
            .options(
                selectinload(DBMolecularDynamicsSimulation.trajectory_frames),
                selectinload(DBMolecularDynamicsSimulation.residue_fluctuations),
                selectinload(DBMolecularDynamicsSimulation.quantum_properties),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_simulations(
        self,
        user_id: Optional[uuid.UUID | str] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        uniprot_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBMolecularDynamicsSimulation]:
        """List simulations filtered by user, workspace, project, or UniProt ID."""
        stmt = (
            select(DBMolecularDynamicsSimulation)
            .options(
                selectinload(DBMolecularDynamicsSimulation.trajectory_frames),
                selectinload(DBMolecularDynamicsSimulation.residue_fluctuations),
                selectinload(DBMolecularDynamicsSimulation.quantum_properties),
            )
            .order_by(desc(DBMolecularDynamicsSimulation.created_at))
            .limit(limit)
            .offset(offset)
        )

        if project_id:
            stmt = stmt.where(DBMolecularDynamicsSimulation.project_id == project_id)
        elif workspace_id:
            stmt = stmt.where(DBMolecularDynamicsSimulation.workspace_id == workspace_id)
        elif user_id:
            stmt = stmt.where(DBMolecularDynamicsSimulation.user_id == user_id)

        if uniprot_id:
            stmt = stmt.where(DBMolecularDynamicsSimulation.uniprot_id == uniprot_id.upper())

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_trajectory_frames(
        self,
        simulation_id: uuid.UUID | str,
        frames_data: List[Dict[str, Any]],
    ) -> List[DBTrajectoryFrame]:
        """Batch add time-series conformational trajectory snapshots."""
        created = []
        for f in frames_data:
            frame = DBTrajectoryFrame(
                id=uuid.uuid4(),
                simulation_id=simulation_id,
                frame_index=int(f.get("frame_index", len(created) + 1)),
                timestamp_ps=float(f.get("timestamp_ps", 0.0)),
                rmsd_angstrom=float(f.get("rmsd_angstrom", 0.0)),
                radius_of_gyration_angstrom=float(f.get("radius_of_gyration_angstrom", 18.5)),
                potential_energy_kj_mol=float(f.get("potential_energy_kj_mol", -450000.0)),
                kinetic_energy_kj_mol=float(f.get("kinetic_energy_kj_mol", 95000.0)),
                total_energy_kj_mol=float(f.get("total_energy_kj_mol", -355000.0)),
                temperature_kelvin=float(f.get("temperature_kelvin", 300.0)),
                frame_pdb_coordinates=str(f.get("frame_pdb_coordinates", "HEADER MD FRAME\nEND\n")),
            )
            self._session.add(frame)
            created.append(frame)
        await self._session.flush()
        return created

    async def add_residue_fluctuations(
        self,
        simulation_id: uuid.UUID | str,
        fluctuations_data: List[Dict[str, Any]],
    ) -> List[DBResidueFluctuation]:
        """Batch add per-residue RMSF flexibility records."""
        created = []
        for r in fluctuations_data:
            fluc = DBResidueFluctuation(
                id=uuid.uuid4(),
                simulation_id=simulation_id,
                residue_number=int(r.get("residue_number", len(created) + 1)),
                residue_name=str(r.get("residue_name", "ALA")),
                rmsf_angstrom=float(r.get("rmsf_angstrom", 1.0)),
                b_factor_equivalent=float(r.get("b_factor_equivalent", 12.0)),
                is_flexible_loop=bool(r.get("is_flexible_loop", False)),
                secondary_structure_type=str(r.get("secondary_structure_type", "helix")),
            )
            self._session.add(fluc)
            created.append(fluc)
        await self._session.flush()
        return created

    async def set_quantum_properties(
        self,
        simulation_id: uuid.UUID | str,
        dft_method: str = "B3LYP/6-31G*",
        homo_energy_ev: float = -6.45,
        lumo_energy_ev: float = -2.15,
        bandgap_energy_ev: float = 4.30,
        dipole_moment_debye: float = 4.82,
        polarizability_angstrom3: float = 142.5,
        total_scf_energy_hartree: float = -2450.85,
        mulliken_partial_charges_json: Optional[Dict[str, Any]] = None,
        electrostatic_potential_surface_json: Optional[Dict[str, Any]] = None,
    ) -> DBQuantumChemistryProperty:
        """Create or update DFT quantum mechanical properties for a simulation."""
        prop = DBQuantumChemistryProperty(
            id=uuid.uuid4(),
            simulation_id=simulation_id,
            dft_method=dft_method,
            homo_energy_ev=homo_energy_ev,
            lumo_energy_ev=lumo_energy_ev,
            bandgap_energy_ev=bandgap_energy_ev,
            dipole_moment_debye=dipole_moment_debye,
            polarizability_angstrom3=polarizability_angstrom3,
            total_scf_energy_hartree=total_scf_energy_hartree,
            mulliken_partial_charges_json=mulliken_partial_charges_json or {},
            electrostatic_potential_surface_json=electrostatic_potential_surface_json or {},
        )
        self._session.add(prop)
        await self._session.flush()
        return prop
