"""SQLAlchemy models for Phase 421: Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DnaPaintNanometerCountingStudy(Base):
    """Study record for Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

    __tablename__ = "p421_dna_paint_nanometer_counting_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Nuclear Pore Complex Scaffold with Fluorescent Imager Strands")
    analytical_modality = Column(String(100), nullable=False, default="dna-paint-counting")
    spatial_localization_precision_nm = Column(Float, nullable=False, default=3.15)
    absolute_molecule_count = Column(Float, nullable=False, default=32.0)
    qpaint_binding_frequency_hz = Column(Float, nullable=False, default=0.42)
    background_dark_time_ratio = Column(Float, nullable=False, default=0.978)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DnaPaintNanometerCountingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DnaPaintNanometerCountingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DnaPaintNanometerCountingItemProfile(Base):
    """Detailed item profile for Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

    __tablename__ = "p421_dna_paint_nanometer_counting_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p421_dna_paint_nanometer_counting_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DnaPaintNanometerCountingStudy", back_populates="item_profiles")


class DnaPaintNanometerCountingMetricTrace(Base):
    """Metric trace for Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

    __tablename__ = "p421_dna_paint_nanometer_counting_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p421_dna_paint_nanometer_counting_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DnaPaintNanometerCountingStudy", back_populates="metric_traces")
