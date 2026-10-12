"""SQLAlchemy models for Phase 440: Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MinfluxNanometerTrackingStudy(Base):
    """Study record for Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

    __tablename__ = "p440_super_resolution_minflux_nanometer_tracking_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Living Motor Protein Myosin V Moving Along Actin Filament with Cy5 Label")
    analytical_modality = Column(String(100), nullable=False, default="minflux-tracking")
    spatial_localization_precision_angstrom = Column(Float, nullable=False, default=8.5)
    temporal_resolution_us = Column(Float, nullable=False, default=120.0)
    photon_budget_efficiency_ratio = Column(Float, nullable=False, default=0.942)
    step_size_hand_over_hand_nm = Column(Float, nullable=False, default=36.2)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MinfluxNanometerTrackingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MinfluxNanometerTrackingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MinfluxNanometerTrackingItemProfile(Base):
    """Detailed item profile for Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

    __tablename__ = "p440_super_resolution_minflux_nanometer_tracking_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p440_super_resolution_minflux_nanometer_tracking_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MinfluxNanometerTrackingStudy", back_populates="item_profiles")


class MinfluxNanometerTrackingMetricTrace(Base):
    """Metric trace for Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

    __tablename__ = "p440_super_resolution_minflux_nanometer_tracking_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p440_super_resolution_minflux_nanometer_tracking_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MinfluxNanometerTrackingStudy", back_populates="metric_traces")
