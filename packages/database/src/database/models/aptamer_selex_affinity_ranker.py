"""SQLAlchemy models for Phase 394: In-Silico Systematic Evolution of Ligands (SELEX) Aptamer Affinity Ranker."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AptamerSelexAffinityRankerStudy(Base):
    """Study record for In-Silico Systematic Evolution of Ligands (SELEX) Aptamer Affinity Ranker."""

    __tablename__ = "p394_selex_ranker_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="aptamer-selex-affinity-ranking")
    aptamer_target_dissociation_constant_kd_nm = Column(Float, nullable=False, default=0.42)
    counter_selex_off_target_discrimination_ratio = Column(Float, nullable=False, default=145.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AptamerSelexAffinityRankerItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("AptamerSelexAffinityRankerMetricTrace", back_populates="study", cascade="all, delete-orphan")


class AptamerSelexAffinityRankerItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p394_selex_ranker_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p394_selex_ranker_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AptamerSelexAffinityRankerStudy", back_populates="item_profiles")


class AptamerSelexAffinityRankerMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p394_selex_ranker_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p394_selex_ranker_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AptamerSelexAffinityRankerStudy", back_populates="metric_traces")
