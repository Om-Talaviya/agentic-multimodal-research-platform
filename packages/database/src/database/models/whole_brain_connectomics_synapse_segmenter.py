"""SQLAlchemy models for Phase 563: Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class WholeBrainConnectomicsSynapseSegmenterStudy(Base):
    """Study record for Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter."""

    __tablename__ = "p563_whole_brain_connectomics_synapse_segmenter_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Serial Section Electron Tomography (FIB-SEM) of Adult Drosophila Melanogaster Central Brain at 4x4x4 nm3 Voxel Resolution")
    analytical_modality = Column(String(100), nullable=False, default="whole-brain-connectomics-segmentation")
    synaptic_junction_detection_f1_score = Column(Float, nullable=False, default=0.982)
    t_bar_active_zone_reconstruction_precision = Column(Float, nullable=False, default=0.978)
    neurite_skeletonization_topological_accuracy = Column(Float, nullable=False, default=0.991)
    segmented_synaptic_density_per_100_um3 = Column(Float, nullable=False, default=84.0)
    confidence_score = Column(Float, nullable=False, default=0.997)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("WholeBrainConnectomicsSynapseSegmenterItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("WholeBrainConnectomicsSynapseSegmenterMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class WholeBrainConnectomicsSynapseSegmenterItemProfile(Base):
    """Detailed item profile for Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter."""

    __tablename__ = "p563_whole_brain_connectomics_synapse_segmenter_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p563_whole_brain_connectomics_synapse_segmenter_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("WholeBrainConnectomicsSynapseSegmenterStudy", back_populates="item_profiles")


class WholeBrainConnectomicsSynapseSegmenterMetricTrace(Base):
    """Metric trace for Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter."""

    __tablename__ = "p563_whole_brain_connectomics_synapse_segmenter_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p563_whole_brain_connectomics_synapse_segmenter_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("WholeBrainConnectomicsSynapseSegmenterStudy", back_populates="metric_traces")
