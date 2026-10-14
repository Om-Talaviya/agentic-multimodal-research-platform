"""SQLAlchemy models for Phase 525: Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CrisprCas12aDirectRnaTargetingDiagnosticsStudy(Base):
    """Study record for Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

    __tablename__ = "p525_crispr_cas12a_direct_rna_targeting_diagnostics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered Dual-Domain Acidaminococcus sp. Cas12a Variant bound to Synthetic SARS-CoV-3 RNA Target")
    analytical_modality = Column(String(100), nullable=False, default="cas12a-direct-rna-cleavage")
    collateral_ssdna_probe_turnover_rate_s_inv = Column(Float, nullable=False, default=240.0)
    single_nucleotide_variant_specificity_ratio = Column(Float, nullable=False, default=85.0)
    limit_of_detection_attomolar_aM = Column(Float, nullable=False, default=15.0)
    isothermal_reaction_kinetic_delay_time_min = Column(Float, nullable=False, default=12.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CrisprCas12aDirectRnaTargetingDiagnosticsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CrisprCas12aDirectRnaTargetingDiagnosticsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CrisprCas12aDirectRnaTargetingDiagnosticsItemProfile(Base):
    """Detailed item profile for Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

    __tablename__ = "p525_crispr_cas12a_direct_rna_targeting_diagnostics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p525_crispr_cas12a_direct_rna_targeting_diagnostics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas12aDirectRnaTargetingDiagnosticsStudy", back_populates="item_profiles")


class CrisprCas12aDirectRnaTargetingDiagnosticsMetricTrace(Base):
    """Metric trace for Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

    __tablename__ = "p525_crispr_cas12a_direct_rna_targeting_diagnostics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p525_crispr_cas12a_direct_rna_targeting_diagnostics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas12aDirectRnaTargetingDiagnosticsStudy", back_populates="metric_traces")
