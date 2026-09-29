"""SQLAlchemy models for Phase 297: Autonomous In-Silico Multi-Specific Nanobody (VHH) Paratope Rigid-Body Conformation Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NanobodyVhhParatopeDesignStudy(Base):
    """Study record for Predicts extended CDR3 loop conformations and non-canonical disulfide bonds in single-domain camelid VHH antibodies, designing humanized multi-specific constructs.."""

    __tablename__ = "nanobody_vhh_design_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="nanobody-vhh-paratope-design")
    vhh_antigen_binding_affinity_retention_pct = Column(Float, nullable=False, default=98.6)
    cdr3_loop_conformation_rmsd_angstrom = Column(Float, nullable=False, default=1.1)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NanobodyVhhParatopeDesignItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("NanobodyVhhParatopeDesignMetricTrace", back_populates="study", cascade="all, delete-orphan")


class NanobodyVhhParatopeDesignItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "nanobody_vhh_design_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("nanobody_vhh_design_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanobodyVhhParatopeDesignStudy", back_populates="item_profiles")


class NanobodyVhhParatopeDesignMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "nanobody_vhh_design_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("nanobody_vhh_design_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanobodyVhhParatopeDesignStudy", back_populates="metric_traces")
