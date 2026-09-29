"""SQLAlchemy models for Phase 354: Autonomous Programmable mRNA Lipid-Polymer Hybrid Nanocapsule Biodistribution & In Vivo Kinetics Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MrnaLipidPolymerNanocapsuleStudy(Base):
    """Study record for Models core-shell lipid-poly(lactic-co-glycolic acid) (PLGA) hybrid nanocapsules conjugated with cell-penetrating peptides for brain-targeted neuroprotective mRNA payload delivery.."""

    __tablename__ = "p354_nanocapsule_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="mrna-lipid-polymer-nanocapsule")
    blood_brain_barrier_transcytosis_efficiency_pct = Column(Float, nullable=False, default=14.8)
    payload_encapsulation_stability_half_life_days = Column(Float, nullable=False, default=45.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MrnaLipidPolymerNanocapsuleItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("MrnaLipidPolymerNanocapsuleMetricTrace", back_populates="study", cascade="all, delete-orphan")


class MrnaLipidPolymerNanocapsuleItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p354_nanocapsule_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p354_nanocapsule_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MrnaLipidPolymerNanocapsuleStudy", back_populates="item_profiles")


class MrnaLipidPolymerNanocapsuleMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p354_nanocapsule_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p354_nanocapsule_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MrnaLipidPolymerNanocapsuleStudy", back_populates="metric_traces")
