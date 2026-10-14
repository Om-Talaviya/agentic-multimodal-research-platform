"""SQLAlchemy models for Phase 486: Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DropletPcrMethylationAmplificationStudy(Base):
    """Study record for Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler."""

    __tablename__ = "p486_droplet_pcr_methylation_amplification_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Bisulfite-Converted ctDNA in 20,000 Microfluidic Fluorinated Oil Picoliter Droplets")
    analytical_modality = Column(String(100), nullable=False, default="droplet-pcr-methylation-amplification")
    fractional_methylation_abundance_pct = Column(Float, nullable=False, default=0.045)
    poisson_droplet_partition_occupancy_lambda = Column(Float, nullable=False, default=0.35)
    false_positive_droplet_count_per_million = Column(Float, nullable=False, default=0.8)
    target_dna_amplification_efficiency = Column(Float, nullable=False, default=0.978)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DropletPcrMethylationAmplificationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DropletPcrMethylationAmplificationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DropletPcrMethylationAmplificationItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler."""

    __tablename__ = "p486_droplet_pcr_methylation_amplification_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p486_droplet_pcr_methylation_amplification_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletPcrMethylationAmplificationStudy", back_populates="item_profiles")


class DropletPcrMethylationAmplificationMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler."""

    __tablename__ = "p486_droplet_pcr_methylation_amplification_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p486_droplet_pcr_methylation_amplification_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletPcrMethylationAmplificationStudy", back_populates="metric_traces")
