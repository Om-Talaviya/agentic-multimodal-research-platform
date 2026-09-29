"""SQLAlchemy models for Phase 344: Autonomous Lipid Nanoparticle (LNP) In Vivo Endosomal Escape & Cytosolic Release Efficiency Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class LnpEndosomalEscapePredictorStudy(Base):
    """Study record for Simulates pH-triggered ionizable lipid protonation, endosomal membrane hexagonal phase transition disruption, and cytosolic mRNA/siRNA delivery payload release kinetics.."""

    __tablename__ = "p344_lnp_escape_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="lnp-endosomal-escape")
    endosomal_escape_fractional_efficiency_pct = Column(Float, nullable=False, default=8.4)
    cytosolic_mrna_translation_half_life_hr = Column(Float, nullable=False, default=28.5)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("LnpEndosomalEscapePredictorItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("LnpEndosomalEscapePredictorMetricTrace", back_populates="study", cascade="all, delete-orphan")


class LnpEndosomalEscapePredictorItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p344_lnp_escape_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p344_lnp_escape_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LnpEndosomalEscapePredictorStudy", back_populates="item_profiles")


class LnpEndosomalEscapePredictorMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p344_lnp_escape_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p344_lnp_escape_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LnpEndosomalEscapePredictorStudy", back_populates="metric_traces")
