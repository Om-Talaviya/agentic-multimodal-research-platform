"""SQLAlchemy models for Phase 573: Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DeepLearningProteinProteinDockingAffinityStudy(Base):
    """Study record for Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

    __tablename__ = "p573_deep_learning_protein_protein_docking_affinity_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="SARS-CoV-2 Spike Receptor-Binding Domain Complexed with Engineered Nanobody Nb21-Fc Variant")
    analytical_modality = Column(String(100), nullable=False, default="se3-diffusion-ppi-docking")
    interface_rmsd_angstrom = Column(Float, nullable=False, default=1.25)
    binding_free_energy_delta_g_kcal_mol = Column(Float, nullable=False, default=-14.8)
    docking_pose_confidence_plddt = Column(Float, nullable=False, default=92.4)
    buried_surface_area_angstrom2 = Column(Float, nullable=False, default=1450.0)
    confidence_score = Column(Float, nullable=False, default=0.998)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DeepLearningProteinProteinDockingAffinityItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DeepLearningProteinProteinDockingAffinityMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DeepLearningProteinProteinDockingAffinityItemProfile(Base):
    """Detailed item profile for Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

    __tablename__ = "p573_deep_learning_protein_protein_docking_affinity_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p573_deep_learning_protein_protein_docking_affinity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DeepLearningProteinProteinDockingAffinityStudy", back_populates="item_profiles")


class DeepLearningProteinProteinDockingAffinityMetricTrace(Base):
    """Metric trace for Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

    __tablename__ = "p573_deep_learning_protein_protein_docking_affinity_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p573_deep_learning_protein_protein_docking_affinity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DeepLearningProteinProteinDockingAffinityStudy", back_populates="metric_traces")
