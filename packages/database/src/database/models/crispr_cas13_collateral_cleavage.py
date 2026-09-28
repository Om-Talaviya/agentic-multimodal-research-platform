"""SQLAlchemy models for Phase 251: Autonomous CRISPR-Cas13 Collateral Cleavage & Viral RNA Detection Specificity Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CrisprCas13CollateralCleavageStudy(Base):
    """Study record for Models Cas13a/Cas13b guide RNA activation, target recognition kinetics, and non-specific bystander collateral ribonuclease activity for ultra-sensitive attomolar pathogen detection.."""

    __tablename__ = "cas13_cleavage_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="crispr-cas13-collateral-cleavage")
    collateral_turnover_rate_kcat_km_s_M = Column(Float, nullable=False, default=12000000.0)
    mismatch_discrimination_ratio = Column(Float, nullable=False, default=48.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CrisprCas13CollateralCleavageItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CrisprCas13CollateralCleavageMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CrisprCas13CollateralCleavageItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "cas13_cleavage_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cas13_cleavage_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas13CollateralCleavageStudy", back_populates="item_profiles")


class CrisprCas13CollateralCleavageMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "cas13_cleavage_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cas13_cleavage_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas13CollateralCleavageStudy", back_populates="metric_traces")
