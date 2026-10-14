"""SQLAlchemy models for Phase 514: Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DeepLearningTcrPmhcDockingEnergyStudy(Base):
    """Study record for Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

    __tablename__ = "p514_deep_learning_tcr_pmhc_docking_energy_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Structure-Resolved Complex of Human CD8+ TCR with Cancer-Testis Neoantigen NY-ESO-1 HLA-A*02:01")
    analytical_modality = Column(String(100), nullable=False, default="egnn-tcr-pmhc-docking")
    predicted_binding_free_energy_delta_G_kcal_mol = Column(Float, nullable=False, default=-10.45)
    cdr3_loop_interface_contact_rmsd_angstrom = Column(Float, nullable=False, default=0.85)
    allotype_cross_reactivity_prediction_auroc = Column(Float, nullable=False, default=0.965)
    dissociation_constant_kd_nM = Column(Float, nullable=False, default=45.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DeepLearningTcrPmhcDockingEnergyItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DeepLearningTcrPmhcDockingEnergyMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DeepLearningTcrPmhcDockingEnergyItemProfile(Base):
    """Detailed item profile for Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

    __tablename__ = "p514_deep_learning_tcr_pmhc_docking_energy_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p514_deep_learning_tcr_pmhc_docking_energy_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DeepLearningTcrPmhcDockingEnergyStudy", back_populates="item_profiles")


class DeepLearningTcrPmhcDockingEnergyMetricTrace(Base):
    """Metric trace for Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

    __tablename__ = "p514_deep_learning_tcr_pmhc_docking_energy_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p514_deep_learning_tcr_pmhc_docking_energy_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DeepLearningTcrPmhcDockingEnergyStudy", back_populates="metric_traces")
