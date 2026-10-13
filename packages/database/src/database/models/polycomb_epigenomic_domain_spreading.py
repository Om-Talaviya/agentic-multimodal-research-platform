"""SQLAlchemy models for Phase 446: Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PolycombEpigenomicDomainStudy(Base):
    """Study record for Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

    __tablename__ = "p446_polycomb_epigenomic_domain_spreading_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Pluripotent Embryonic Stem Cells Differentiation Locus Chromatin Super-Domain")
    analytical_modality = Column(String(100), nullable=False, default="polycomb-epigenomic-spreading")
    polycomb_spreading_velocity_bp_per_hr = Column(Float, nullable=False, default=1450.0)
    prc2_nucleosome_occupancy_ratio = Column(Float, nullable=False, default=0.895)
    chromatin_compaction_density_nm = Column(Float, nullable=False, default=28.4)
    transcriptional_repression_half_life_days = Column(Float, nullable=False, default=6.8)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("PolycombEpigenomicDomainItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("PolycombEpigenomicDomainMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class PolycombEpigenomicDomainItemProfile(Base):
    """Detailed item profile for Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

    __tablename__ = "p446_polycomb_epigenomic_domain_spreading_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p446_polycomb_epigenomic_domain_spreading_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PolycombEpigenomicDomainStudy", back_populates="item_profiles")


class PolycombEpigenomicDomainMetricTrace(Base):
    """Metric trace for Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

    __tablename__ = "p446_polycomb_epigenomic_domain_spreading_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p446_polycomb_epigenomic_domain_spreading_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PolycombEpigenomicDomainStudy", back_populates="metric_traces")
