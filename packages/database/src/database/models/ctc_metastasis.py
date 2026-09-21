"""CTC Models (Phase 111)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBCirculatingTumorCellSample(Base):
    __tablename__ = "ctc_samples"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    patient_id = Column(String(100), nullable=False)
    primary_tumor_type = Column(String(100), nullable=False)
    ctc_enumeration_per_7_5ml = Column(Integer, default=18, nullable=False)
    emt_hybrid_score = Column(Float, default=0.74, nullable=False)
    metastatic_tropism_primary = Column(String(100), default="Hepatic", nullable=False)
    capture_technology = Column(String(100), default="Microfluidic Vortex Chip", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    colonization_sites = relationship("DBMetastaticColonizationSite", back_populates="ctc_sample", cascade="all, delete-orphan")

class DBMetastaticColonizationSite(Base):
    __tablename__ = "ctc_colonization_sites"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ctc_sample_id = Column(GUID(), ForeignKey("ctc_samples.id", ondelete="CASCADE"), nullable=False, index=True)
    target_organ = Column(String(100), nullable=False)
    colonization_probability = Column(Float, nullable=False)
    seed_soil_compatibility_score = Column(Float, default=82.4, nullable=False)
    chemokine_gradient_strength = Column(Float, default=0.88, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ctc_sample = relationship("DBCirculatingTumorCellSample", back_populates="colonization_sites")
