"""SQLAlchemy models for Phase 390: Autonomous Allosteric Cryptic Pocket Transient Opening & Molecular Dynamics Markov State Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AllostericCrypticPocketMsmStudy(Base):
    """Study record for Constructs microsecond-scale Markov State Models (MSM) from enhanced sampling molecular dynamics to capture transiently opening cryptic binding pockets invisible in static crystallography.."""

    __tablename__ = "p390_cryptic_msm_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="allosteric-cryptic-pocket-msm")
    cryptic_pocket_opening_transition_timescale_ns = Column(Float, nullable=False, default=450.0)
    pocket_druggability_score_site_map = Column(Float, nullable=False, default=1.18)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AllostericCrypticPocketMsmItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("AllostericCrypticPocketMsmMetricTrace", back_populates="study", cascade="all, delete-orphan")


class AllostericCrypticPocketMsmItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p390_cryptic_msm_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p390_cryptic_msm_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AllostericCrypticPocketMsmStudy", back_populates="item_profiles")


class AllostericCrypticPocketMsmMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p390_cryptic_msm_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p390_cryptic_msm_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AllostericCrypticPocketMsmStudy", back_populates="metric_traces")
