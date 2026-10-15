"""SQLAlchemy models for Phase 528: Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class HighSpeedAfmMolecularMotorDynamicsStudy(Base):
    """Study record for Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

    __tablename__ = "p528_high_speed_afm_molecular_motor_dynamics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Single Native Myosin V Dimer stepping along Immobilized Actin Filament in Microfluidic HS-AFM Cell")
    analytical_modality = Column(String(100), nullable=False, default="hs-afm-molecular-motor")
    hand_over_hand_step_distance_nm = Column(Float, nullable=False, default=36.2)
    power_stroke_lever_arm_rotation_deg = Column(Float, nullable=False, default=72.0)
    afm_cantilever_imaging_rate_fps = Column(Float, nullable=False, default=12.5)
    atp_limited_dwell_time_ms = Column(Float, nullable=False, default=42.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("HighSpeedAfmMolecularMotorDynamicsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("HighSpeedAfmMolecularMotorDynamicsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class HighSpeedAfmMolecularMotorDynamicsItemProfile(Base):
    """Detailed item profile for Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

    __tablename__ = "p528_high_speed_afm_molecular_motor_dynamics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p528_high_speed_afm_molecular_motor_dynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HighSpeedAfmMolecularMotorDynamicsStudy", back_populates="item_profiles")


class HighSpeedAfmMolecularMotorDynamicsMetricTrace(Base):
    """Metric trace for Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

    __tablename__ = "p528_high_speed_afm_molecular_motor_dynamics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p528_high_speed_afm_molecular_motor_dynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HighSpeedAfmMolecularMotorDynamicsStudy", back_populates="metric_traces")
