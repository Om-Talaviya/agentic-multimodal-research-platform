"""SQLAlchemy models for Phase 507: Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MetabolicRetrosynthesisXenobiologyStudy(Base):
    """Study record for Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

    __tablename__ = "p507_metabolic_retrosynthesis_xenobiology_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes")
    analytical_modality = Column(String(100), nullable=False, default="xenobiotic-retrosynthesis-flux")
    retrosynthetic_pathway_plausibility_score = Column(Float, nullable=False, default=0.942)
    thermodynamic_driving_force_delta_G_kj_mol = Column(Float, nullable=False, default=-34.8)
    theoretical_maximum_carbon_yield_pct = Column(Float, nullable=False, default=92.5)
    chassis_endogenous_flux_perturbation_index = Column(Float, nullable=False, default=0.125)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MetabolicRetrosynthesisXenobiologyItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MetabolicRetrosynthesisXenobiologyMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MetabolicRetrosynthesisXenobiologyItemProfile(Base):
    """Detailed item profile for Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

    __tablename__ = "p507_metabolic_retrosynthesis_xenobiology_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p507_metabolic_retrosynthesis_xenobiology_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MetabolicRetrosynthesisXenobiologyStudy", back_populates="item_profiles")


class MetabolicRetrosynthesisXenobiologyMetricTrace(Base):
    """Metric trace for Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

    __tablename__ = "p507_metabolic_retrosynthesis_xenobiology_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p507_metabolic_retrosynthesis_xenobiology_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MetabolicRetrosynthesisXenobiologyStudy", back_populates="metric_traces")
