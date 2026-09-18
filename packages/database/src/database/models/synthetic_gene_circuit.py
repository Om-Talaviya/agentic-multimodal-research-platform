"""Synthetic Biology Gene Circuit & Boolean Logic Gate Database Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBSyntheticGeneCircuit(Base):
    __tablename__ = "synthetic_gene_circuits"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    circuit_name = Column(String(255), nullable=False)
    chassis_organism = Column(String(100), default="Escherichia coli K-12", nullable=False)
    logic_function = Column(String(100), default="AND", nullable=False)  # AND, OR, NAND, NOR, XOR
    input_signals = Column(JSON, default=list, nullable=False)  # ["aTc", "IPTG"]
    output_reporter = Column(String(100), default="sfGFP", nullable=False)
    assembly_standard = Column(String(50), default="Golden Gate (MoClo)", nullable=False)
    plasmid_size_bp = Column(Integer, default=5400, nullable=False)
    on_off_dynamic_range = Column(Float, default=12.5, nullable=False)  # Fold induction
    circuit_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    gates = relationship("DBBioLogicGate", back_populates="circuit", cascade="all, delete-orphan")
    kinetics_traces = relationship("DBCircuitKineticsTrace", back_populates="circuit", cascade="all, delete-orphan")


class DBBioLogicGate(Base):
    __tablename__ = "bio_logic_gates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    circuit_id = Column(GUID(), ForeignKey("synthetic_gene_circuits.id", ondelete="CASCADE"), nullable=False, index=True)
    gate_name = Column(String(100), nullable=False)
    gate_type = Column(String(50), nullable=False)  # NOT, AND, NOR, etc.
    promoter_part = Column(String(100), nullable=False)  # e.g., pTet, pLac, pLux
    repressor_activator = Column(String(100), nullable=False)  # TetR, LacI, LuxR
    rbs_strength = Column(Float, default=1.0, nullable=False)
    hill_coefficient_n = Column(Float, default=2.2, nullable=False)
    kd_dissociation_uM = Column(Float, default=0.15, nullable=False)
    overhang_5p = Column(String(20), default="AATG", nullable=False)
    overhang_3p = Column(String(20), default="AGCT", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    circuit = relationship("DBSyntheticGeneCircuit", back_populates="gates")


class DBCircuitKineticsTrace(Base):
    __tablename__ = "circuit_kinetics_traces"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    circuit_id = Column(GUID(), ForeignKey("synthetic_gene_circuits.id", ondelete="CASCADE"), nullable=False, index=True)
    state_condition = Column(String(100), nullable=False)  # e.g. "Input_00", "Input_11"
    simulation_duration_min = Column(Float, default=360.0, nullable=False)
    steady_state_expression_au = Column(Float, nullable=False)
    response_half_time_min = Column(Float, default=45.0, nullable=False)
    time_series_data = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    circuit = relationship("DBSyntheticGeneCircuit", back_populates="kinetics_traces")
