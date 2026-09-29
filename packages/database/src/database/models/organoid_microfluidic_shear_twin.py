"""SQLAlchemy models for Phase 341: Autonomous In Silico Organoid Microfluidic Shear Stress & Nutrient Diffusion Twin."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OrganoidMicrofluidicShearTwinStudy(Base):
    """Study record for Simulates Navier-Stokes fluid shear stresses, oxygen transport gradients, and metabolic waste clearance across microfluidic channels containing 3D vascularized human brain/kidney organoids.."""

    __tablename__ = "microfluidic_shear_twin_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="organoid-microfluidic-twin")
    physiologic_wall_shear_stress_dynes_cm2 = Column(Float, nullable=False, default=15.4)
    core_hypoxia_volume_fraction_pct = Column(Float, nullable=False, default=1.85)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OrganoidMicrofluidicShearTwinItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("OrganoidMicrofluidicShearTwinMetricTrace", back_populates="study", cascade="all, delete-orphan")


class OrganoidMicrofluidicShearTwinItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "microfluidic_shear_twin_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("microfluidic_shear_twin_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganoidMicrofluidicShearTwinStudy", back_populates="item_profiles")


class OrganoidMicrofluidicShearTwinMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "microfluidic_shear_twin_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("microfluidic_shear_twin_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganoidMicrofluidicShearTwinStudy", back_populates="metric_traces")
