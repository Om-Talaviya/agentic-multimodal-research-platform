"""Quantum Chemistry & Molecular Hamiltonian VQE Simulation Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base


class DBQuantumMolecularSystem(Base):
    __tablename__ = "quantum_molecular_systems"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    molecule_name = Column(String(255), nullable=False)
    smiles_formula = Column(String(255), default="H2")
    basis_set = Column(String(64), default="STO-3G")
    charge = Column(Integer, default=0)
    multiplicity = Column(Integer, default=1)
    num_qubits = Column(Integer, default=4)
    active_electrons = Column(Integer, default=2)
    active_orbitals = Column(Integer, default=2)
    nuclear_repulsion_energy = Column(Float, default=0.71375)
    geometry_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    ansatz_executions = relationship("DBVQEAnsatzExecution", back_populates="system", cascade="all, delete-orphan")
    energy_states = relationship("DBHamiltonianEnergyState", back_populates="system", cascade="all, delete-orphan")


class DBVQEAnsatzExecution(Base):
    __tablename__ = "vqe_ansatz_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String(36), ForeignKey("quantum_molecular_systems.id", ondelete="CASCADE"), nullable=False)
    ansatz_type = Column(String(64), default="UCCSD")
    optimizer_algorithm = Column(String(64), default="COBYLA")
    ground_state_energy_hartree = Column(Float, default=-1.137)
    exact_fci_energy_hartree = Column(Float, default=-1.1373)
    energy_error_kcal_mol = Column(Float, default=0.188)
    chemical_accuracy_reached = Column(Boolean, default=True)
    iteration_count = Column(Integer, default=42)
    execution_time_seconds = Column(Float, default=1.25)
    optimal_parameters_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    system = relationship("DBQuantumMolecularSystem", back_populates="ansatz_executions")


class DBHamiltonianEnergyState(Base):
    __tablename__ = "hamiltonian_energy_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String(36), ForeignKey("quantum_molecular_systems.id", ondelete="CASCADE"), nullable=False)
    state_label = Column(String(64), default="Ground State (S0)")
    expectation_energy = Column(Float, default=-1.137)
    dipole_moment_debye = Column(Float, default=0.0)
    spin_multiplicity = Column(Integer, default=1)
    is_ground_state = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    system = relationship("DBQuantumMolecularSystem", back_populates="energy_states")
