"""SQLAlchemy models for Phase 517: Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MultiplexedOptogeneticNeocorticalSynchronyStudy(Base):
    """Study record for Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

    __tablename__ = "p517_multiplexed_optogenetic_neocortical_synchrony_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Transgenic Mouse Somatosensory Cortex expressing ChRmine (Red) and ChETA (Blue) in Layer 2/3 and 5")
    analytical_modality = Column(String(100), nullable=False, default="dual-color-optogenetic-synchrony")
    gamma_band_phase_locking_value_plv = Column(Float, nullable=False, default=0.895)
    optical_crosstalk_attenuation_ratio = Column(Float, nullable=False, default=42.0)
    spike_timing_jitter_precision_std_ms = Column(Float, nullable=False, default=0.45)
    cross_layer_laminar_information_transfer_entropy = Column(Float, nullable=False, default=0.68)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MultiplexedOptogeneticNeocorticalSynchronyItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MultiplexedOptogeneticNeocorticalSynchronyMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MultiplexedOptogeneticNeocorticalSynchronyItemProfile(Base):
    """Detailed item profile for Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

    __tablename__ = "p517_multiplexed_optogenetic_neocortical_synchrony_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p517_multiplexed_optogenetic_neocortical_synchrony_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MultiplexedOptogeneticNeocorticalSynchronyStudy", back_populates="item_profiles")


class MultiplexedOptogeneticNeocorticalSynchronyMetricTrace(Base):
    """Metric trace for Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

    __tablename__ = "p517_multiplexed_optogenetic_neocortical_synchrony_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p517_multiplexed_optogenetic_neocortical_synchrony_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MultiplexedOptogeneticNeocorticalSynchronyStudy", back_populates="metric_traces")
