"""SQLAlchemy models for Phase 557: Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimeResolvedXfelStructuralDynamicsStudy(Base):
    """Study record for Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

    __tablename__ = "p557_time_resolved_xfel_structural_dynamics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Photoactive Yellow Protein (PYP) Microcrystals probed by 10-fs X-ray Pulses at LCLS-II after 450nm Laser Photolysis")
    analytical_modality = Column(String(100), nullable=False, default="time-resolved-xfel-dynamics")
    femtosecond_temporal_resolution_fs = Column(Float, nullable=False, default=85.0)
    chromophore_trans_to_cis_isomerization_time_ps = Column(Float, nullable=False, default=1.45)
    difference_electron_density_signal_snr = Column(Float, nullable=False, default=28.5)
    serial_femtosecond_crystallography_resolution_a = Column(Float, nullable=False, default=1.35)
    confidence_score = Column(Float, nullable=False, default=0.997)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("TimeResolvedXfelStructuralDynamicsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("TimeResolvedXfelStructuralDynamicsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class TimeResolvedXfelStructuralDynamicsItemProfile(Base):
    """Detailed item profile for Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

    __tablename__ = "p557_time_resolved_xfel_structural_dynamics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p557_time_resolved_xfel_structural_dynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("TimeResolvedXfelStructuralDynamicsStudy", back_populates="item_profiles")


class TimeResolvedXfelStructuralDynamicsMetricTrace(Base):
    """Metric trace for Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

    __tablename__ = "p557_time_resolved_xfel_structural_dynamics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p557_time_resolved_xfel_structural_dynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("TimeResolvedXfelStructuralDynamicsStudy", back_populates="metric_traces")
