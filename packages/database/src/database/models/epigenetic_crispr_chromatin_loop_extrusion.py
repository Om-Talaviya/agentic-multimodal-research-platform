"""SQLAlchemy models for Phase 515: Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class EpigeneticCrisprChromatinLoopExtrusionStudy(Base):
    """Study record for Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

    __tablename__ = "p515_epigenetic_crispr_chromatin_loop_extrusion_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human K562 Cells with Chemically Dimerizable dCas9-CTCF Targeted to MYC Super-Enhancer TAD")
    analytical_modality = Column(String(100), nullable=False, default="crispr-chromatin-loop-rewriting")
    induced_chromatin_loop_contact_frequency_enhancement = Column(Float, nullable=False, default=4.2)
    insulation_boundary_score_gain = Column(Float, nullable=False, default=0.825)
    target_oncogene_expression_activation_fold = Column(Float, nullable=False, default=5.4)
    cohesin_retention_time_at_engineered_ctcf_min = Column(Float, nullable=False, default=38.0)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("EpigeneticCrisprChromatinLoopExtrusionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("EpigeneticCrisprChromatinLoopExtrusionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class EpigeneticCrisprChromatinLoopExtrusionItemProfile(Base):
    """Detailed item profile for Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

    __tablename__ = "p515_epigenetic_crispr_chromatin_loop_extrusion_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p515_epigenetic_crispr_chromatin_loop_extrusion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EpigeneticCrisprChromatinLoopExtrusionStudy", back_populates="item_profiles")


class EpigeneticCrisprChromatinLoopExtrusionMetricTrace(Base):
    """Metric trace for Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

    __tablename__ = "p515_epigenetic_crispr_chromatin_loop_extrusion_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p515_epigenetic_crispr_chromatin_loop_extrusion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EpigeneticCrisprChromatinLoopExtrusionStudy", back_populates="metric_traces")
