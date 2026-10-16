"""SQLAlchemy models for Phase 552: Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DenovoRbsTranslationInitiationOptimizerStudy(Base):
    """Study record for Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

    __tablename__ = "p552_denovo_rbs_translation_initiation_optimizer_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Synthetic mRNA Polycistronic Operon 5' UTR Shine-Dalgarno Core Library in Escherichia coli BL21(DE3)")
    analytical_modality = Column(String(100), nullable=False, default="de-novo-rbs-optimization")
    translation_initiation_rate_arbitrary_units = Column(Float, nullable=False, default=48500.0)
    rna_secondary_structure_free_energy_kcal_mol = Column(Float, nullable=False, default=-14.8)
    shine_dalgarno_16s_rrna_hybridization_energy = Column(Float, nullable=False, default=-9.4)
    cross_cistronic_translational_coupling_ratio = Column(Float, nullable=False, default=0.88)
    confidence_score = Column(Float, nullable=False, default=0.997)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DenovoRbsTranslationInitiationOptimizerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DenovoRbsTranslationInitiationOptimizerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DenovoRbsTranslationInitiationOptimizerItemProfile(Base):
    """Detailed item profile for Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

    __tablename__ = "p552_denovo_rbs_translation_initiation_optimizer_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p552_denovo_rbs_translation_initiation_optimizer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DenovoRbsTranslationInitiationOptimizerStudy", back_populates="item_profiles")


class DenovoRbsTranslationInitiationOptimizerMetricTrace(Base):
    """Metric trace for Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

    __tablename__ = "p552_denovo_rbs_translation_initiation_optimizer_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p552_denovo_rbs_translation_initiation_optimizer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DenovoRbsTranslationInitiationOptimizerStudy", back_populates="metric_traces")
