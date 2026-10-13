"""SQLAlchemy models for Phase 466: Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OptogeneticRheotaxisMicroSwarmStudy(Base):
    """Study record for Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler."""

    __tablename__ = "p466_optogenetic_rheotaxis_micro_swarm_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered B. subtilis Swarm with Light-Gated Flagellar Torque Switch in Laminar Microfluidic Channel")
    analytical_modality = Column(String(100), nullable=False, default="optogenetic-rheotaxis-swarm")
    micro_swarm_upstream_drift_velocity_um_s = Column(Float, nullable=False, default=14.8)
    bioconvective_plume_wavelength_um = Column(Float, nullable=False, default=125.0)
    light_stimulated_phototactic_bias_ratio = Column(Float, nullable=False, default=3.42)
    vorticity_enstrophy_metric = Column(Float, nullable=False, default=0.925)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OptogeneticRheotaxisMicroSwarmItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OptogeneticRheotaxisMicroSwarmMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OptogeneticRheotaxisMicroSwarmItemProfile(Base):
    """Detailed item profile for Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler."""

    __tablename__ = "p466_optogenetic_rheotaxis_micro_swarm_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p466_optogenetic_rheotaxis_micro_swarm_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticRheotaxisMicroSwarmStudy", back_populates="item_profiles")


class OptogeneticRheotaxisMicroSwarmMetricTrace(Base):
    """Metric trace for Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler."""

    __tablename__ = "p466_optogenetic_rheotaxis_micro_swarm_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p466_optogenetic_rheotaxis_micro_swarm_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticRheotaxisMicroSwarmStudy", back_populates="metric_traces")
