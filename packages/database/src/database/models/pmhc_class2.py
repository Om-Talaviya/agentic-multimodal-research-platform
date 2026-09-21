"""MHC Class II Models (Phase 118)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBMHCClass2Screen(Base):
    __tablename__ = "mhc_class2_screens"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    hla_class2_allele = Column(String(50), nullable=False)
    source_protein_antigen = Column(String(100), nullable=False)
    total_screened_15mers = Column(Integer, default=240, nullable=False)
    immunogenic_hits_count = Column(Integer, default=14, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    neoepitopes = relationship("DBCD4NeoepitopeHit", back_populates="screen", cascade="all, delete-orphan")

class DBCD4NeoepitopeHit(Base):
    __tablename__ = "mhc_class2_neoepitopes"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("mhc_class2_screens.id", ondelete="CASCADE"), nullable=False, index=True)
    peptide_15mer_sequence = Column(String(30), nullable=False)
    core_9mer_binding_motif = Column(String(20), nullable=False)
    binding_affinity_ic50_nm = Column(Float, nullable=False)
    cd4_immunogenicity_tier = Column(String(50), default="STRONG_BINDER", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    screen = relationship("DBMHCClass2Screen", back_populates="neoepitopes")
