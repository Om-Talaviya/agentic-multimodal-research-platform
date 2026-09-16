"""
SQLAlchemy models for Synthetic Biology DNA Circuit Design & Logic Gate Compiler (Phase 65).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBSyntheticCircuitDesign(Base):
    """Represents an engineered synthetic biological DNA logic circuit."""
    __tablename__ = "synbio_circuits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    circuit_name = Column(String(128), nullable=False)
    host_organism = Column(String(64), default="E. coli K-12 (MG1655)")
    logic_expression = Column(String(128), default="A AND B")  # e.g., (A AND B) NOR C
    gate_topology = Column(String(64), default="Two-Input AND Gate")
    total_parts = Column(Integer, default=0)
    dynamic_range_on_off_ratio = Column(Float, default=42.5)
    sbol_xml_preview = Column(Text, nullable=True)
    status = Column(String(32), default="COMPILED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    parts = relationship("DBGeneticPart", back_populates="circuit", cascade="all, delete-orphan")
    truth_table = relationship("DBCircuitTruthTableEntry", back_populates="circuit", cascade="all, delete-orphan")


class DBGeneticPart(Base):
    """Represents a characterized bio-brick part (promoter, RBS, CDS, terminator)."""
    __tablename__ = "synbio_genetic_parts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    circuit_id = Column(String(36), ForeignKey("synbio_circuits.id", ondelete="CASCADE"), nullable=False)
    part_type = Column(String(32), nullable=False)  # Promoter, RBS, CDS, Terminator
    part_name = Column(String(64), nullable=False)  # pTac, BBa_B0034, TetR, LacI, T1
    part_sequence = Column(String(255), nullable=False)
    order_index = Column(Integer, default=1)
    relative_strength_au = Column(Float, default=1.0)
    repressor_affinity_kd_um = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    circuit = relationship("DBSyntheticCircuitDesign", back_populates="parts")


class DBCircuitTruthTableEntry(Base):
    """Represents the characterized or simulated truth table output for a circuit."""
    __tablename__ = "synbio_truth_table_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    circuit_id = Column(String(36), ForeignKey("synbio_circuits.id", ondelete="CASCADE"), nullable=False)
    input_state_a = Column(Boolean, default=False)
    input_state_b = Column(Boolean, default=False)
    expected_output = Column(Boolean, default=False)
    simulated_fluorescence_rfu = Column(Float, nullable=False)
    response_delay_minutes = Column(Float, default=25.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    circuit = relationship("DBSyntheticCircuitDesign", back_populates="truth_table")
