"""SQLAlchemy models for Phase 356: Autonomous High-Throughput Droplet Microfluidic Single-Cell Antibody Screening Sorter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DropletMicrofluidicAntibodyStudy(Base):
    """Study record for Simulates picoliter aqueous-in-oil droplet encapsulation, fluorescence-activated droplet sorting (FADS), and single-cell plasma cell secretome IgG binding kinetics at 10,000 droplets per second.."""

    __tablename__ = "p356_droplet_ab_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="droplet-microfluidic-antibody")
    droplet_sorting_throughput_droplets_per_sec = Column(Float, nullable=False, default=10000.0)
    single_cell_encapsulation_monodispersity_pct = Column(Float, nullable=False, default=99.4)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DropletMicrofluidicAntibodyItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("DropletMicrofluidicAntibodyMetricTrace", back_populates="study", cascade="all, delete-orphan")


class DropletMicrofluidicAntibodyItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p356_droplet_ab_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p356_droplet_ab_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletMicrofluidicAntibodyStudy", back_populates="item_profiles")


class DropletMicrofluidicAntibodyMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p356_droplet_ab_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p356_droplet_ab_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletMicrofluidicAntibodyStudy", back_populates="metric_traces")
