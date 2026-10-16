"""SQLAlchemy models for Phase 572: Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OptogeneticNeuromodulatoryGpcReceptorActivatorStudy(Base):
    """Study record for Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""

    __tablename__ = "p572_optogenetic_neuromodulatory_gpc_receptor_activator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Opto-beta2-Adrenergic Receptor Chimeric Constructs Expressed in Primary Hippocampal Neurons")
    analytical_modality = Column(String(100), nullable=False, default="opto-gpcr-second-messenger-modeling")
    camp_generation_rate_nm_s = Column(Float, nullable=False, default=42.5)
    g_protein_coupling_selectivity = Column(Float, nullable=False, default=0.965)
    photocurrent_deactivation_tau_ms = Column(Float, nullable=False, default=145.0)
    downstream_phosphorylation_index = Column(Float, nullable=False, default=0.912)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OptogeneticNeuromodulatoryGpcReceptorActivatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OptogeneticNeuromodulatoryGpcReceptorActivatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OptogeneticNeuromodulatoryGpcReceptorActivatorItemProfile(Base):
    """Detailed item profile for Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""

    __tablename__ = "p572_optogenetic_neuromodulatory_gpc_receptor_activator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p572_optogenetic_neuromodulatory_gpc_receptor_activator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticNeuromodulatoryGpcReceptorActivatorStudy", back_populates="item_profiles")


class OptogeneticNeuromodulatoryGpcReceptorActivatorMetricTrace(Base):
    """Metric trace for Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""

    __tablename__ = "p572_optogenetic_neuromodulatory_gpc_receptor_activator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p572_optogenetic_neuromodulatory_gpc_receptor_activator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticNeuromodulatoryGpcReceptorActivatorStudy", back_populates="metric_traces")
