"""SQLAlchemy models for Phase 427: Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CgbeCas12fMiniatureEditingStudy(Base):
    """Study record for Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

    __tablename__ = "p427_cgbe_cas12f_miniature_editing_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Ultra-Compact Cas12f Miniature CGBE Complex in AAV Vector")
    analytical_modality = Column(String(100), nullable=False, default="cgbe-cas12f-editing")
    c_to_g_conversion_purity_percent = Column(Float, nullable=False, default=88.6)
    on_target_indel_frequency_percent = Column(Float, nullable=False, default=2.1)
    aav_packaging_size_kb = Column(Float, nullable=False, default=4.25)
    off_target_cleavage_fraction = Column(Float, nullable=False, default=0.0035)
    confidence_score = Column(Float, nullable=False, default=0.987)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CgbeCas12fMiniatureEditingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CgbeCas12fMiniatureEditingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CgbeCas12fMiniatureEditingItemProfile(Base):
    """Detailed item profile for Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

    __tablename__ = "p427_cgbe_cas12f_miniature_editing_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p427_cgbe_cas12f_miniature_editing_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CgbeCas12fMiniatureEditingStudy", back_populates="item_profiles")


class CgbeCas12fMiniatureEditingMetricTrace(Base):
    """Metric trace for Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

    __tablename__ = "p427_cgbe_cas12f_miniature_editing_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p427_cgbe_cas12f_miniature_editing_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CgbeCas12fMiniatureEditingStudy", back_populates="metric_traces")
