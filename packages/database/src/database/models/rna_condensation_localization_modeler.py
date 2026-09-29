"""SQLAlchemy models for Phase 321: Autonomous Intracellular RNA Zipcode Localization & Liquid-Liquid Phase Separation Condensate Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class RnaCondensationLocalizationModelerStudy(Base):
    """Study record for Predicts RNA 3' UTR zipcode motifs governing motor-protein transport and multivalent RNA-protein condensation into stress granules and P-bodies.."""

    __tablename__ = "rna_condensate_loc_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="rna-condensation-localization")
    condensate_partition_coefficient_k = Column(Float, nullable=False, default=48.0)
    motor_protein_binding_affinity_kd_nm = Column(Float, nullable=False, default=12.4)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("RnaCondensationLocalizationModelerItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("RnaCondensationLocalizationModelerMetricTrace", back_populates="study", cascade="all, delete-orphan")


class RnaCondensationLocalizationModelerItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "rna_condensate_loc_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("rna_condensate_loc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RnaCondensationLocalizationModelerStudy", back_populates="item_profiles")


class RnaCondensationLocalizationModelerMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "rna_condensate_loc_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("rna_condensate_loc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RnaCondensationLocalizationModelerStudy", back_populates="metric_traces")
