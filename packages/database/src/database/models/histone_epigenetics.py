"""Histone Models (Phase 112)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBHistoneChIPSample(Base):
    __tablename__ = "histone_chip_samples"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    sample_name = Column(String(100), nullable=False)
    histone_mark = Column(String(50), nullable=False)
    cell_line_or_tissue = Column(String(100), nullable=False)
    total_aligned_peaks = Column(Integer, default=14500, nullable=False)
    super_enhancer_count = Column(Integer, default=285, nullable=False)
    frip_score = Column(Float, default=0.38, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    super_enhancers = relationship("DBSuperEnhancerLocus", back_populates="chip_sample", cascade="all, delete-orphan")

class DBSuperEnhancerLocus(Base):
    __tablename__ = "histone_super_enhancers"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    chip_sample_id = Column(GUID(), ForeignKey("histone_chip_samples.id", ondelete="CASCADE"), nullable=False, index=True)
    locus_coordinates = Column(String(100), nullable=False)
    associated_oncogene = Column(String(100), nullable=False)
    rose_ranking_score = Column(Float, nullable=False)
    signal_intensity_rpm = Column(Float, default=1450.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chip_sample = relationship("DBHistoneChIPSample", back_populates="super_enhancers")
