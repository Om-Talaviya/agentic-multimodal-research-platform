"""SQLAlchemy models for Phase 571: Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleCellSpatialEpigenomicCutAndTagStudy(Base):
    """Study record for Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""

    __tablename__ = "p571_single_cell_spatial_epigenomic_cut_and_tag_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Murine Embryonic Cortex Cryosection Microfluidic Deterministic Barcoding CUT&Tag for H3K27me3 and H3K4me3")
    analytical_modality = Column(String(100), nullable=False, default="spatial-cut-and-tag-epigenomics")
    chromatin_enrichment_specificity = Column(Float, nullable=False, default=9.4)
    spatial_barcoding_purity = Column(Float, nullable=False, default=0.975)
    signal_to_background_promoter_ratio = Column(Float, nullable=False, default=18.2)
    niche_clustering_silhouette = Column(Float, nullable=False, default=0.885)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleCellSpatialEpigenomicCutAndTagItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleCellSpatialEpigenomicCutAndTagMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleCellSpatialEpigenomicCutAndTagItemProfile(Base):
    """Detailed item profile for Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""

    __tablename__ = "p571_single_cell_spatial_epigenomic_cut_and_tag_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p571_single_cell_spatial_epigenomic_cut_and_tag_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCellSpatialEpigenomicCutAndTagStudy", back_populates="item_profiles")


class SingleCellSpatialEpigenomicCutAndTagMetricTrace(Base):
    """Metric trace for Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""

    __tablename__ = "p571_single_cell_spatial_epigenomic_cut_and_tag_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p571_single_cell_spatial_epigenomic_cut_and_tag_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCellSpatialEpigenomicCutAndTagStudy", back_populates="metric_traces")
