"""SQLAlchemy models for Phase 471: Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SomatogenesisHes7ClockWavefrontStudy(Base):
    """Study record for Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

    __tablename__ = "p471_somatogenesis_hes7_clock_wavefront_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Synthetic Presomitic Mesoderm (PSM) Microtissue Organoid with Oscillatory Hes7-Venus Reporter")
    analytical_modality = Column(String(100), nullable=False, default="somatogenesis-clock-wavefront")
    clock_oscillation_periodicity_minutes = Column(Float, nullable=False, default=124.0)
    wavefront_propagation_velocity_um_per_hr = Column(Float, nullable=False, default=48.5)
    somite_boundary_sharpness_contrast_ratio = Column(Float, nullable=False, default=4.15)
    synchronization_kuramoto_order_parameter = Column(Float, nullable=False, default=0.942)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SomatogenesisHes7ClockWavefrontItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SomatogenesisHes7ClockWavefrontMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SomatogenesisHes7ClockWavefrontItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

    __tablename__ = "p471_somatogenesis_hes7_clock_wavefront_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p471_somatogenesis_hes7_clock_wavefront_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SomatogenesisHes7ClockWavefrontStudy", back_populates="item_profiles")


class SomatogenesisHes7ClockWavefrontMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

    __tablename__ = "p471_somatogenesis_hes7_clock_wavefront_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p471_somatogenesis_hes7_clock_wavefront_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SomatogenesisHes7ClockWavefrontStudy", back_populates="metric_traces")
