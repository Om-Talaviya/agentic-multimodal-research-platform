"""Spatial MSI Models (Phase 116)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBSpatialMSISample(Base):
    __tablename__ = "spatial_msi_samples"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    tissue_section_name = Column(String(100), nullable=False)
    msi_modality = Column(String(100), default="MALDI-MSI (FT-ICR)", nullable=False)
    spatial_resolution_microns = Column(Float, default=20.0, nullable=False)
    total_mz_features = Column(Integer, default=1840, nullable=False)
    warburg_lactate_gradient_ratio = Column(Float, default=3.42, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    metabolite_gradients = relationship("DBTissueMetaboliteGradient", back_populates="msi_sample", cascade="all, delete-orphan")

class DBTissueMetaboliteGradient(Base):
    __tablename__ = "spatial_msi_gradients"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    msi_sample_id = Column(GUID(), ForeignKey("spatial_msi_samples.id", ondelete="CASCADE"), nullable=False, index=True)
    metabolite_name = Column(String(100), nullable=False)
    mz_ratio = Column(Float, nullable=False)
    tumor_core_intensity = Column(Float, nullable=False)
    stromal_border_intensity = Column(Float, nullable=False)
    core_to_border_ratio = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    msi_sample = relationship("DBSpatialMSISample", back_populates="metabolite_gradients")
