"""SQLAlchemy models for Phase 487: Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SnareComplexDynamicZipperingStudy(Base):
    """Study record for Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor."""

    __tablename__ = "p487_snare_complex_dynamic_zippering_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Reconstituted Proteoliposome Single-Vesicle Synaptobrevin-2 / Syntaxin-1A / SNAP-25 Assembly")
    analytical_modality = Column(String(100), nullable=False, default="snare-complex-zippering")
    snare_zippering_free_energy_kbT = Column(Float, nullable=False, default=35.0)
    membrane_fusion_pore_opening_time_ms = Column(Float, nullable=False, default=0.85)
    synaptotagmin_ca2_activation_threshold_uM = Column(Float, nullable=False, default=12.5)
    vesicle_docking_priming_probability = Column(Float, nullable=False, default=0.942)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SnareComplexDynamicZipperingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SnareComplexDynamicZipperingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SnareComplexDynamicZipperingItemProfile(Base):
    """Detailed item profile for Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor."""

    __tablename__ = "p487_snare_complex_dynamic_zippering_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p487_snare_complex_dynamic_zippering_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SnareComplexDynamicZipperingStudy", back_populates="item_profiles")


class SnareComplexDynamicZipperingMetricTrace(Base):
    """Metric trace for Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor."""

    __tablename__ = "p487_snare_complex_dynamic_zippering_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p487_snare_complex_dynamic_zippering_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SnareComplexDynamicZipperingStudy", back_populates="metric_traces")
