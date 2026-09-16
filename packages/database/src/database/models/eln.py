"""
SQLAlchemy models for Autonomous Multi-Modal Electronic Lab Notebook (ELN) (Phase 53).
Implements FDA 21 CFR Part 11 compliant tamper-evident audit trails, digital witness signatures,
and dynamic multi-modal experiment blocks (SMILES, protocols, charts, markdown).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBElectronicLabNotebook(Base):
    """Represents an Electronic Lab Notebook (ELN) experiment entry."""
    __tablename__ = "eln_notebooks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    author_id = Column(String(64), nullable=False, default="researcher_user")
    status = Column(String(50), nullable=False, default="DRAFT")  # DRAFT, UNDER_REVIEW, WITNESSED, ARCHIVED
    tags = Column(JSON, nullable=False, default=list)
    cfr_part11_signed = Column(Boolean, default=False)
    witness_signature = Column(JSON, nullable=True)  # {signer_id, timestamp, sha256_hash, statement}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    blocks = relationship(
        "DBLabNotebookBlock",
        back_populates="notebook",
        cascade="all, delete-orphan",
        order_by="DBLabNotebookBlock.order_index.asc()",
    )
    audit_trails = relationship(
        "DBELNAuditTrailEntry",
        back_populates="notebook",
        cascade="all, delete-orphan",
        order_by="DBELNAuditTrailEntry.timestamp.desc()",
    )


class DBLabNotebookBlock(Base):
    """Represents a modular multimodal content block inside an ELN notebook."""
    __tablename__ = "eln_blocks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    notebook_id = Column(String(36), ForeignKey("eln_notebooks.id", ondelete="CASCADE"), nullable=False, index=True)
    block_type = Column(String(50), nullable=False)  # MARKDOWN, PROTOCOL_STEP, MOLECULAR_SMILES, DATASET_VIEWER, CHART_WIDGET
    order_index = Column(Integer, nullable=False, default=0)
    content_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notebook = relationship("DBElectronicLabNotebook", back_populates="blocks")


class DBELNAuditTrailEntry(Base):
    """Immutable ALCOA+ & 21 CFR Part 11 compliant audit trail record with cryptographic chaining."""
    __tablename__ = "eln_audit_trails"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    notebook_id = Column(String(36), ForeignKey("eln_notebooks.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(String(64), nullable=False)
    action = Column(String(100), nullable=False)  # BLOCK_INSERT, BLOCK_UPDATE, WITNESS_SIGN, STATUS_CHANGE
    diff_payload = Column(JSON, nullable=False, default=dict)
    cryptographic_hash = Column(String(64), nullable=False)  # SHA-256 tamper-evident digest
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notebook = relationship("DBElectronicLabNotebook", back_populates="audit_trails")
