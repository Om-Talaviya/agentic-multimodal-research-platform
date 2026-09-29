"""SQLAlchemy models for Phase 346: Autonomous Pharmacogenomic HLA-Allele Drug Hypersensitivity & Adverse Reaction Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class HlaDrugHypersensitivityProfilerStudy(Base):
    """Study record for Models pharmacological altered repertoire and direct p-i binding of small molecules into the antigen-recognition grooves of polymorphic HLA Class I & II alleles (e.g. HLA-B*57:01, HLA-B*15:02).."""

    __tablename__ = "p346_hla_hyper_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="hla-drug-hypersensitivity")
    hla_allele_adverse_hypersensitivity_risk_score = Column(Float, nullable=False, default=99.1)
    altered_peptide_repertoire_binding_affinity_nm = Column(Float, nullable=False, default=18.2)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("HlaDrugHypersensitivityProfilerItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("HlaDrugHypersensitivityProfilerMetricTrace", back_populates="study", cascade="all, delete-orphan")


class HlaDrugHypersensitivityProfilerItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p346_hla_hyper_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p346_hla_hyper_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HlaDrugHypersensitivityProfilerStudy", back_populates="item_profiles")


class HlaDrugHypersensitivityProfilerMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p346_hla_hyper_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p346_hla_hyper_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HlaDrugHypersensitivityProfilerStudy", back_populates="metric_traces")
