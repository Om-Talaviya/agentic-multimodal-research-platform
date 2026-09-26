"""SQLAlchemy models for Phase 219: Autonomous Synthetic mRNA 5' Cap Structure & Poly(A) Tail Deadenylation Decay Kinetics Simulator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MrnaCapPolyADecayStudy(Base):
    """Study record for Models synthetic mRNA translation initiation efficiency and half-life dynamics as a function of Cap-1/Cap-2 enzymatic structures and poly(A) deadenylation rate kinetics.."""

    __tablename__ = "mrna_cap_polya_decay_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="mrna-cap-poly-a-decay")
    mrna_half_life_hours = Column(Float, nullable=False, default=38.6)
    initiation_complex_affinity_kd_nM = Column(Float, nullable=False, default=14.2)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MrnaCapPolyADecayItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("MrnaCapPolyADecayMetricTrace", back_populates="study", cascade="all, delete-orphan")


class MrnaCapPolyADecayItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "mrna_cap_polya_decay_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("mrna_cap_polya_decay_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MrnaCapPolyADecayStudy", back_populates="item_profiles")


class MrnaCapPolyADecayMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "mrna_cap_polya_decay_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("mrna_cap_polya_decay_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MrnaCapPolyADecayStudy", back_populates="metric_traces")
