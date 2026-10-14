"""SQLAlchemy models for Phase 498: Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class XnaNcaaExpandedGeneticCodeStudy(Base):
    """Study record for Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

    __tablename__ = "p498_xna_ncaa_expanded_genetic_code_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Orthogonal Methionyl-tRNA Synthetase / tRNA Pair in Recoded E. coli C321.deltaA with UAG Amber Suppression")
    analytical_modality = Column(String(100), nullable=False, default="expanded-genetic-code-translation")
    ncaa_incorporation_fidelity_pct = Column(Float, nullable=False, default=99.1)
    amber_uag_suppression_efficiency = Column(Float, nullable=False, default=0.895)
    orthogonal_synthetase_catalytic_kcat_over_km = Column(Float, nullable=False, default=18500.0)
    recombinant_protein_expression_yield_mg_per_L = Column(Float, nullable=False, default=42.5)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("XnaNcaaExpandedGeneticCodeItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("XnaNcaaExpandedGeneticCodeMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class XnaNcaaExpandedGeneticCodeItemProfile(Base):
    """Detailed item profile for Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

    __tablename__ = "p498_xna_ncaa_expanded_genetic_code_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p498_xna_ncaa_expanded_genetic_code_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("XnaNcaaExpandedGeneticCodeStudy", back_populates="item_profiles")


class XnaNcaaExpandedGeneticCodeMetricTrace(Base):
    """Metric trace for Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

    __tablename__ = "p498_xna_ncaa_expanded_genetic_code_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p498_xna_ncaa_expanded_genetic_code_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("XnaNcaaExpandedGeneticCodeStudy", back_populates="metric_traces")
