"""SQLAlchemy models for Phase 461: Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NotchDeltaTensionTransducerStudy(Base):
    """Study record for Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer."""

    __tablename__ = "p461_notch_delta_tension_transducer_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Synthetic SynNotch Engineered Fibroblast Dual-Lattice Cell Sorting Array")
    analytical_modality = Column(String(100), nullable=False, default="notch-delta-mechanotransduction")
    mechanical_pulling_force_pico_newtons = Column(Float, nullable=False, default=12.8)
    s2_s3_cleavage_transcription_activation_ratio = Column(Float, nullable=False, default=8.65)
    lateral_inhibition_bistability_index = Column(Float, nullable=False, default=0.925)
    boundary_sharpening_transition_width_cell_diameters = Column(Float, nullable=False, default=1.4)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NotchDeltaTensionTransducerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NotchDeltaTensionTransducerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NotchDeltaTensionTransducerItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer."""

    __tablename__ = "p461_notch_delta_tension_transducer_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p461_notch_delta_tension_transducer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NotchDeltaTensionTransducerStudy", back_populates="item_profiles")


class NotchDeltaTensionTransducerMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer."""

    __tablename__ = "p461_notch_delta_tension_transducer_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p461_notch_delta_tension_transducer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NotchDeltaTensionTransducerStudy", back_populates="metric_traces")
