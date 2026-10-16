"""SQLAlchemy models for Phase 564: Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AcousticMicrostreamingSonoporationEngineStudy(Base):
    """Study record for Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

    __tablename__ = "p564_acoustic_microstreaming_sonoporation_engine_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Suspended Human CD34+ Hematopoietic Stem Cells and Phospholipid Microbubbles subjected to 1-MHz Focused Acoustic Waves")
    analytical_modality = Column(String(100), nullable=False, default="acoustic-microstreaming-sonoporation")
    intracellular_delivery_efficiency_pct = Column(Float, nullable=False, default=92.4)
    cell_membrane_resealing_time_seconds = Column(Float, nullable=False, default=38.0)
    acoustic_cavitation_shear_stress_kpa = Column(Float, nullable=False, default=18.5)
    post_sonoporation_cell_viability_pct = Column(Float, nullable=False, default=94.8)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AcousticMicrostreamingSonoporationEngineItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("AcousticMicrostreamingSonoporationEngineMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class AcousticMicrostreamingSonoporationEngineItemProfile(Base):
    """Detailed item profile for Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

    __tablename__ = "p564_acoustic_microstreaming_sonoporation_engine_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p564_acoustic_microstreaming_sonoporation_engine_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticMicrostreamingSonoporationEngineStudy", back_populates="item_profiles")


class AcousticMicrostreamingSonoporationEngineMetricTrace(Base):
    """Metric trace for Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

    __tablename__ = "p564_acoustic_microstreaming_sonoporation_engine_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p564_acoustic_microstreaming_sonoporation_engine_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticMicrostreamingSonoporationEngineStudy", back_populates="metric_traces")
