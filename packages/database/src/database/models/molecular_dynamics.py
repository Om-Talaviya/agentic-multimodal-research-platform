"""Autonomous Molecular Dynamics (MD) & Quantum Chemistry Simulation Database Models (Phase 39)."""

import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBMolecularDynamicsSimulation(Base):
    """Master simulation specification for all-atom conformational MD trajectories and quantum DFT calculations."""

    __tablename__ = "md_simulations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)

    uniprot_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    system_name: Mapped[str] = mapped_column(String(255), nullable=False)
    organism: Mapped[str] = mapped_column(String(128), default="Homo sapiens")
    forcefield: Mapped[str] = mapped_column(String(64), default="AMBER14SB")  # AMBER14SB, CHARMM36m, OPLS_AA
    solvent_model: Mapped[str] = mapped_column(String(64), default="TIP3P")    # TIP3P, OPC, implicit_GB
    ensemble: Mapped[str] = mapped_column(String(32), default="NPT")          # NPT, NVT, NVE

    total_frames: Mapped[int] = mapped_column(Integer, default=50)
    timestep_ps: Mapped[float] = mapped_column(Float, default=2.0)
    total_duration_ns: Mapped[float] = mapped_column(Float, default=100.0)
    temperature_kelvin: Mapped[float] = mapped_column(Float, default=300.0)
    pressure_bar: Mapped[float] = mapped_column(Float, default=1.013)

    equilibrium_rmsd_angstrom: Mapped[float] = mapped_column(Float, default=1.42)
    energy_minimization_converged: Mapped[bool] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="completed")  # running, completed, failed

    thermodynamic_data_json: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    trajectory_frames: Mapped[List["DBTrajectoryFrame"]] = relationship(
        "DBTrajectoryFrame",
        back_populates="simulation",
        cascade="all, delete-orphan",
        order_by="DBTrajectoryFrame.frame_index",
    )
    residue_fluctuations: Mapped[List["DBResidueFluctuation"]] = relationship(
        "DBResidueFluctuation",
        back_populates="simulation",
        cascade="all, delete-orphan",
        order_by="DBResidueFluctuation.residue_number",
    )
    quantum_properties: Mapped[Optional["DBQuantumChemistryProperty"]] = relationship(
        "DBQuantumChemistryProperty",
        back_populates="simulation",
        uselist=False,
        cascade="all, delete-orphan",
    )


class DBTrajectoryFrame(Base):
    """Individual time-series conformational coordinate snapshot in a molecular dynamics trajectory."""

    __tablename__ = "md_trajectory_frames"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("md_simulations.id", ondelete="CASCADE"), nullable=False, index=True)

    frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_ps: Mapped[float] = mapped_column(Float, nullable=False)
    rmsd_angstrom: Mapped[float] = mapped_column(Float, default=0.0)
    radius_of_gyration_angstrom: Mapped[float] = mapped_column(Float, default=18.5)

    potential_energy_kj_mol: Mapped[float] = mapped_column(Float, default=-450000.0)
    kinetic_energy_kj_mol: Mapped[float] = mapped_column(Float, default=95000.0)
    total_energy_kj_mol: Mapped[float] = mapped_column(Float, default=-355000.0)
    temperature_kelvin: Mapped[float] = mapped_column(Float, default=300.0)

    frame_pdb_coordinates: Mapped[str] = mapped_column(Text, nullable=False)

    simulation: Mapped["DBMolecularDynamicsSimulation"] = relationship("DBMolecularDynamicsSimulation", back_populates="trajectory_frames")


class DBResidueFluctuation(Base):
    """Root Mean Square Fluctuation (RMSF) per-residue flexibility and mobility curve."""

    __tablename__ = "md_residue_fluctuations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("md_simulations.id", ondelete="CASCADE"), nullable=False, index=True)

    residue_number: Mapped[int] = mapped_column(Integer, nullable=False)
    residue_name: Mapped[str] = mapped_column(String(8), nullable=False)
    rmsf_angstrom: Mapped[float] = mapped_column(Float, nullable=False)
    b_factor_equivalent: Mapped[float] = mapped_column(Float, default=12.5)
    is_flexible_loop: Mapped[bool] = mapped_column(Integer, default=0)
    secondary_structure_type: Mapped[str] = mapped_column(String(16), default="helix")  # helix, sheet, loop

    simulation: Mapped["DBMolecularDynamicsSimulation"] = relationship("DBMolecularDynamicsSimulation", back_populates="residue_fluctuations")


class DBQuantumChemistryProperty(Base):
    """Quantum Mechanical Density Functional Theory (DFT) electronic properties and orbital energies."""

    __tablename__ = "md_quantum_properties"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("md_simulations.id", ondelete="CASCADE"), nullable=False, index=True)

    dft_method: Mapped[str] = mapped_column(String(64), default="B3LYP/6-31G*")
    homo_energy_ev: Mapped[float] = mapped_column(Float, nullable=False)          # Highest Occupied Molecular Orbital
    lumo_energy_ev: Mapped[float] = mapped_column(Float, nullable=False)          # Lowest Unoccupied Molecular Orbital
    bandgap_energy_ev: Mapped[float] = mapped_column(Float, nullable=False)      # LUMO - HOMO
    dipole_moment_debye: Mapped[float] = mapped_column(Float, default=4.82)
    polarizability_angstrom3: Mapped[float] = mapped_column(Float, default=142.5)
    total_scf_energy_hartree: Mapped[float] = mapped_column(Float, default=-2450.85)

    mulliken_partial_charges_json: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)
    electrostatic_potential_surface_json: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)

    simulation: Mapped["DBMolecularDynamicsSimulation"] = relationship("DBMolecularDynamicsSimulation", back_populates="quantum_properties")
