"""SQLAlchemy models for Phase 457: Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BiohybridSoftActuatorMyotubeStudy(Base):
    """Study record for Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

    __tablename__ = "p457_biohybrid_soft_actuator_myotube_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="3D Bioprinted Optogenetic C2C12 Skeletal Myotube Cantilever on Flexible Hydrogel Skeleton")
    analytical_modality = Column(String(100), nullable=False, default="biohybrid-actuator-mechanics")
    active_contractile_force_micro_newtons = Column(Float, nullable=False, default=285.0)
    twitch_to_tetanus_force_ratio = Column(Float, nullable=False, default=0.34)
    cyclic_fatigue_endurance_cycles = Column(Float, nullable=False, default=12500.0)
    electromechanical_coupling_efficiency = Column(Float, nullable=False, default=0.912)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BiohybridSoftActuatorMyotubeItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BiohybridSoftActuatorMyotubeMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BiohybridSoftActuatorMyotubeItemProfile(Base):
    """Detailed item profile for Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

    __tablename__ = "p457_biohybrid_soft_actuator_myotube_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p457_biohybrid_soft_actuator_myotube_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BiohybridSoftActuatorMyotubeStudy", back_populates="item_profiles")


class BiohybridSoftActuatorMyotubeMetricTrace(Base):
    """Metric trace for Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

    __tablename__ = "p457_biohybrid_soft_actuator_myotube_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p457_biohybrid_soft_actuator_myotube_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BiohybridSoftActuatorMyotubeStudy", back_populates="metric_traces")
