"""SQLAlchemy models for Phase 381: Autonomous Single-Cell DNA Methylation and Hydroxymethylation (5mC/5hmC) Bisulfite-Free Caller."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Singlecell5mc5hmcCallerStudy(Base):
    """Study record for Resolves 5-methylcytosine (5mC) versus 5-hydroxymethylcytosine (5hmC) at base-pair single-cell resolution using enzymatic TET-assisted pyridine borane sequencing (TAPS).."""

    __tablename__ = "p381_5mc_5hmc_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="singlecell-5mc-5hmc-caller")
    base_resolution_5hmc_calling_precision_pct = Column(Float, nullable=False, default=98.4)
    single_cell_cpg_site_coverage_depth_fold = Column(Float, nullable=False, default=12.5)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("Singlecell5mc5hmcCallerItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("Singlecell5mc5hmcCallerMetricTrace", back_populates="study", cascade="all, delete-orphan")


class Singlecell5mc5hmcCallerItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p381_5mc_5hmc_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p381_5mc_5hmc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("Singlecell5mc5hmcCallerStudy", back_populates="item_profiles")


class Singlecell5mc5hmcCallerMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p381_5mc_5hmc_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p381_5mc_5hmc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("Singlecell5mc5hmcCallerStudy", back_populates="metric_traces")
