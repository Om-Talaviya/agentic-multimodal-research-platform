"""SQLAlchemy models for Phase 458: Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OrganOnChipMicrovascularShearStudy(Base):
    """Study record for Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

    __tablename__ = "p458_organ_on_chip_microvascular_shear_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Dual-Channel Microfluidic Blood-Brain Barrier Chip with Pericytes and Endothelial Shear")
    analytical_modality = Column(String(100), nullable=False, default="microvascular-fluid-shear")
    wall_shear_stress_dynes_per_cm2 = Column(Float, nullable=False, default=14.8)
    transendothelial_electrical_resistance_teer_ohm_cm2 = Column(Float, nullable=False, default=1850.0)
    dextran_permeability_coefficient_cm_per_s = Column(Float, nullable=False, default=1.2e-05)
    endothelial_alignment_angle_std_deg = Column(Float, nullable=False, default=8.4)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OrganOnChipMicrovascularShearItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OrganOnChipMicrovascularShearMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OrganOnChipMicrovascularShearItemProfile(Base):
    """Detailed item profile for Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

    __tablename__ = "p458_organ_on_chip_microvascular_shear_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p458_organ_on_chip_microvascular_shear_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganOnChipMicrovascularShearStudy", back_populates="item_profiles")


class OrganOnChipMicrovascularShearMetricTrace(Base):
    """Metric trace for Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

    __tablename__ = "p458_organ_on_chip_microvascular_shear_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p458_organ_on_chip_microvascular_shear_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganOnChipMicrovascularShearStudy", back_populates="metric_traces")
