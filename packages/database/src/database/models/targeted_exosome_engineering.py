"""SQLAlchemy models for Phase 373: Autonomous Targeted Exosome Surface Engineering & Blood-Brain Barrier Transcytosis Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TargetedExosomeEngineeringStudy(Base):
    """Study record for Simulates Lamp2b-RVG peptide surface display, CD63 tetraspanin membrane anchor stability, and receptor-mediated transcytosis across human brain microvascular endothelial cells.."""

    __tablename__ = "p373_exosome_eng_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="targeted-exosome-engineering")
    blood_brain_barrier_transcytosis_rate_pct = Column(Float, nullable=False, default=18.2)
    vesicle_colloidal_stability_zeta_potential_mv = Column(Float, nullable=False, default=28.5)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("TargetedExosomeEngineeringItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("TargetedExosomeEngineeringMetricTrace", back_populates="study", cascade="all, delete-orphan")


class TargetedExosomeEngineeringItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p373_exosome_eng_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p373_exosome_eng_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("TargetedExosomeEngineeringStudy", back_populates="item_profiles")


class TargetedExosomeEngineeringMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p373_exosome_eng_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p373_exosome_eng_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("TargetedExosomeEngineeringStudy", back_populates="metric_traces")
