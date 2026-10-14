"""SQLAlchemy models for Phase 522: Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SuperResolutionExpansionCryoMicroscopyStudy(Base):
    """Study record for Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler."""

    __tablename__ = "p522_super_resolution_expansion_cryo_microscopy_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="4x Polyacrylate Hydrogel Swollen Vitrified Mouse Hippocampal Synapse with Pre- and Post-Synaptic Markers")
    analytical_modality = Column(String(100), nullable=False, default="cryo-expansion-super-resolution")
    effective_isotropic_optical_resolution_nm = Column(Float, nullable=False, default=14.5)
    macromolecular_isotropy_expansion_factor = Column(Float, nullable=False, default=4.15)
    fluorescent_label_retention_efficiency_pct = Column(Float, nullable=False, default=92.0)
    clem_spatial_registration_fiducial_error_nm = Column(Float, nullable=False, default=8.5)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SuperResolutionExpansionCryoMicroscopyItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SuperResolutionExpansionCryoMicroscopyMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SuperResolutionExpansionCryoMicroscopyItemProfile(Base):
    """Detailed item profile for Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler."""

    __tablename__ = "p522_super_resolution_expansion_cryo_microscopy_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p522_super_resolution_expansion_cryo_microscopy_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SuperResolutionExpansionCryoMicroscopyStudy", back_populates="item_profiles")


class SuperResolutionExpansionCryoMicroscopyMetricTrace(Base):
    """Metric trace for Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler."""

    __tablename__ = "p522_super_resolution_expansion_cryo_microscopy_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p522_super_resolution_expansion_cryo_microscopy_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SuperResolutionExpansionCryoMicroscopyStudy", back_populates="metric_traces")
