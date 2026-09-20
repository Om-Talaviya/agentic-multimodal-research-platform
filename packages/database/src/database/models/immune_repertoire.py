"""
SQLAlchemy database models for Phase 104: Immune Repertoire & TCR/BCR Clonotype Profiling.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID

class DBImmuneRepertoire(Base):
    __tablename__ = "immune_repertoires"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    sample_name = Column(String(255), nullable=False, index=True)
    organism = Column(String(100), default="Homo sapiens")
    chain_type = Column(String(50), default="TCR_ALPHA_BETA", index=True)
    clonotype_count = Column(Integer, default=0)
    total_cells = Column(Integer, default=0)
    shannon_entropy = Column(Float, default=0.0)
    gini_simpson_index = Column(Float, default=0.0)
    clonality_score = Column(Float, default=0.0)
    metadata_json = Column(JSON, nullable=True)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clonotypes = relationship("DBTCRClonotype", back_populates="repertoire", cascade="all, delete-orphan")
    vdj_pairings = relationship("DBVDJRecombination", back_populates="repertoire", cascade="all, delete-orphan")

class DBTCRClonotype(Base):
    __tablename__ = "tcr_clonotypes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    repertoire_id = Column(GUID(), ForeignKey("immune_repertoires.id", ondelete="CASCADE"), nullable=False, index=True)
    cdr3_nt = Column(String(255), nullable=True)
    cdr3_aa = Column(String(100), nullable=False, index=True)
    v_gene = Column(String(50), nullable=False, index=True)
    d_gene = Column(String(50), nullable=True)
    j_gene = Column(String(50), nullable=False, index=True)
    c_gene = Column(String(50), nullable=True)
    frequency = Column(Float, default=0.0)
    count = Column(Integer, default=1)
    is_productive = Column(Boolean, default=True)
    antigen_specificity = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    repertoire = relationship("DBImmuneRepertoire", back_populates="clonotypes")

class DBVDJRecombination(Base):
    __tablename__ = "vdj_recombinations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    repertoire_id = Column(GUID(), ForeignKey("immune_repertoires.id", ondelete="CASCADE"), nullable=False, index=True)
    v_family = Column(String(50), nullable=False, index=True)
    j_family = Column(String(50), nullable=False, index=True)
    pairing_frequency = Column(Float, default=0.0)
    cdr3_length = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)

    repertoire = relationship("DBImmuneRepertoire", back_populates="vdj_pairings")
