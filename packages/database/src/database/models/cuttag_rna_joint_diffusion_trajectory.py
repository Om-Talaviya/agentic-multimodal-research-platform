"""SQLAlchemy models for Phase 495: Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CuttagRnaJointDiffusionTrajectoryStudy(Base):
    """Study record for Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

    __tablename__ = "p495_cuttag_rna_joint_diffusion_trajectory_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Developing Murine Cortical Plate Radial Glia Lineage with H3K4me3 / H3K27ac and mRNA Co-Assay")
    analytical_modality = Column(String(100), nullable=False, default="cuttag-rna-joint-diffusion")
    epigenomic_chromatin_velocity_coherence = Column(Float, nullable=False, default=0.932)
    promoter_enhancer_concordance_score = Column(Float, nullable=False, default=0.895)
    diffusion_pseudotime_lineage_resolution_tau = Column(Float, nullable=False, default=0.965)
    joint_latent_space_neighbor_overlap_pct = Column(Float, nullable=False, default=94.2)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CuttagRnaJointDiffusionTrajectoryItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CuttagRnaJointDiffusionTrajectoryMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CuttagRnaJointDiffusionTrajectoryItemProfile(Base):
    """Detailed item profile for Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

    __tablename__ = "p495_cuttag_rna_joint_diffusion_trajectory_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p495_cuttag_rna_joint_diffusion_trajectory_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CuttagRnaJointDiffusionTrajectoryStudy", back_populates="item_profiles")


class CuttagRnaJointDiffusionTrajectoryMetricTrace(Base):
    """Metric trace for Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

    __tablename__ = "p495_cuttag_rna_joint_diffusion_trajectory_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p495_cuttag_rna_joint_diffusion_trajectory_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CuttagRnaJointDiffusionTrajectoryStudy", back_populates="metric_traces")
