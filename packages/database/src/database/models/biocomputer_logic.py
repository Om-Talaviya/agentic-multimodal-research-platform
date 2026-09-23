"""
Phase 131: Synthetic Gene Logic Biocomputer & Multi-Input Cellular State Classifier Database Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBBiocomputerCircuit(Base):
    """Represents a multi-input synthetic gene logic biocomputer circuit."""

    __tablename__ = "biocomputer_circuits"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    circuit_name = Column(String(200), nullable=False, index=True)
    target_cell_type = Column(String(150), nullable=False)
    logic_expression = Column(String(300), nullable=False)  # e.g., "(miR-21 AND NOT miR-141) OR (EpCAM AND Myc)"
    truth_table = Column(JSON, nullable=False, default=dict)
    gate_count = Column(Integer, default=4, nullable=False)
    noise_margin_db = Column(Float, default=14.5, nullable=False)
    metadata_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    gates = relationship(
        "DBLogicGateCascade",
        back_populates="circuit",
        cascade="all, delete-orphan",
        order_by="DBLogicGateCascade.created_at",
    )
    classifiers = relationship(
        "DBCellularStateClassifier",
        back_populates="circuit",
        cascade="all, delete-orphan",
        order_by="DBCellularStateClassifier.created_at",
    )


class DBLogicGateCascade(Base):
    """Represents an individual biological logic gate node in the circuit cascade."""

    __tablename__ = "logic_gate_cascades"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    circuit_id = Column(GUID(), ForeignKey("biocomputer_circuits.id", ondelete="CASCADE"), nullable=False, index=True)
    gate_id = Column(String(100), nullable=False)
    gate_type = Column(String(50), nullable=False)  # AND, OR, NOR, NAND, NOT, XOR
    promoter_repressor_pair = Column(String(200), nullable=False)
    km_uM = Column(Float, default=2.5, nullable=False)
    hill_n = Column(Float, default=2.8, nullable=False)
    signal_delay_mins = Column(Float, default=45.0, nullable=False)
    state_high_output_rfu = Column(Float, default=4800.0, nullable=False)
    state_low_output_rfu = Column(Float, default=120.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    circuit = relationship("DBBiocomputerCircuit", back_populates="gates")


class DBCellularStateClassifier(Base):
    """Represents a diagnostic/therapeutic cellular classifier classifying diseased vs healthy states."""

    __tablename__ = "cellular_state_classifiers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    circuit_id = Column(GUID(), ForeignKey("biocomputer_circuits.id", ondelete="CASCADE"), nullable=False, index=True)
    classifier_name = Column(String(200), nullable=False)
    input_biomarkers = Column(JSON, nullable=False, default=list)  # list of marker names/miRNAs
    output_payload = Column(String(200), nullable=False)  # e.g., "tBid_Apoptosis_Inducer" or "GFP_Reporter"
    classification_accuracy = Column(Float, default=0.96, nullable=False)
    false_positive_rate = Column(Float, default=0.03, nullable=False)
    auc_roc = Column(Float, default=0.985, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    circuit = relationship("DBBiocomputerCircuit", back_populates="classifiers")
