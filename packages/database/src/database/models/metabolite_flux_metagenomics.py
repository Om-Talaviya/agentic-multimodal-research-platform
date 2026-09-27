"""SQLAlchemy models for Phase 225: Autonomous Metagenomic Metabolic Flux & Gut-Liver Axis Co-Metabolism Simulator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MetaboliteFluxMetagenomicsStudy(Base):
    """Study record for Integrates whole-metagenome shotgun sequencing with multi-species flux balance analysis to forecast short-chain fatty acid and bile acid biotransformations across the gut-liver axis.."""

    __tablename__ = "meta_flux_metagenome_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="metabolite-flux-metagenomics")
    scfa_butyrate_production_mmol_gDW_h = Column(Float, nullable=False, default=14.8)
    microbiome_host_flux_coupling_index = Column(Float, nullable=False, default=0.92)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MetaboliteFluxMetagenomicsItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("MetaboliteFluxMetagenomicsMetricTrace", back_populates="study", cascade="all, delete-orphan")


class MetaboliteFluxMetagenomicsItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "meta_flux_metagenome_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("meta_flux_metagenome_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MetaboliteFluxMetagenomicsStudy", back_populates="item_profiles")


class MetaboliteFluxMetagenomicsMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "meta_flux_metagenome_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("meta_flux_metagenome_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MetaboliteFluxMetagenomicsStudy", back_populates="metric_traces")
