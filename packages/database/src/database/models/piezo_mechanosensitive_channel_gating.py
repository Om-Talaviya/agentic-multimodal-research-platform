"""SQLAlchemy models for Phase 494: Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PiezoMechanosensitiveChannelGatingStudy(Base):
    """Study record for Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

    __tablename__ = "p494_piezo_mechanosensitive_channel_gating_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="High-Speed Pressure Clamped HEK293 Cell expressing Human PIEZO1 Trimeric Propeller Blades")
    analytical_modality = Column(String(100), nullable=False, default="piezo-mechanosensitive-gating")
    half_maximal_activation_tension_mN_per_m = Column(Float, nullable=False, default=2.85)
    channel_open_probability_p_open = Column(Float, nullable=False, default=0.945)
    single_channel_conductance_pS = Column(Float, nullable=False, default=29.5)
    mechanical_inactivation_tau_ms = Column(Float, nullable=False, default=16.2)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("PiezoMechanosensitiveChannelGatingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("PiezoMechanosensitiveChannelGatingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class PiezoMechanosensitiveChannelGatingItemProfile(Base):
    """Detailed item profile for Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

    __tablename__ = "p494_piezo_mechanosensitive_channel_gating_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p494_piezo_mechanosensitive_channel_gating_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PiezoMechanosensitiveChannelGatingStudy", back_populates="item_profiles")


class PiezoMechanosensitiveChannelGatingMetricTrace(Base):
    """Metric trace for Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

    __tablename__ = "p494_piezo_mechanosensitive_channel_gating_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p494_piezo_mechanosensitive_channel_gating_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PiezoMechanosensitiveChannelGatingStudy", back_populates="metric_traces")
