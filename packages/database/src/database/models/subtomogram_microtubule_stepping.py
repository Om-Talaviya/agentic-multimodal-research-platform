"""SQLAlchemy models for Phase 418: Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SubtomogramMicrotubuleSteppingStudy(Base):
    """Study record for Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

    __tablename__ = "p418_subtomogram_microtubule_stepping_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Axonemal 13-Protofilament Microtubule with Kinesin-1 Dimers")
    analytical_modality = Column(String(100), nullable=False, default="subtomogram-microtubule")
    subtomogram_resolution_angstrom = Column(Float, nullable=False, default=3.85)
    motor_step_size_nm = Column(Float, nullable=False, default=8.12)
    protofilament_twist_angle_deg = Column(Float, nullable=False, default=0.28)
    stepping_dwell_time_ms = Column(Float, nullable=False, default=18.5)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SubtomogramMicrotubuleSteppingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SubtomogramMicrotubuleSteppingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SubtomogramMicrotubuleSteppingItemProfile(Base):
    """Detailed item profile for Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

    __tablename__ = "p418_subtomogram_microtubule_stepping_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p418_subtomogram_microtubule_stepping_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SubtomogramMicrotubuleSteppingStudy", back_populates="item_profiles")


class SubtomogramMicrotubuleSteppingMetricTrace(Base):
    """Metric trace for Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

    __tablename__ = "p418_subtomogram_microtubule_stepping_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p418_subtomogram_microtubule_stepping_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SubtomogramMicrotubuleSteppingStudy", back_populates="metric_traces")
