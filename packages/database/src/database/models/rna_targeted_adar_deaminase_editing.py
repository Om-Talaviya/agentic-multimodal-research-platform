"""SQLAlchemy models for Phase 566: Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class RnaTargetedAdarDeaminaseEditingStudy(Base):
    """Study record for Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

    __tablename__ = "p566_rna_targeted_adar_deaminase_editing_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Endogenous Human ADAR2 Deaminase recruited via Circular Guide RNA (arRNA) targeting Premature Stop Codons in MECP2 mRNA")
    analytical_modality = Column(String(100), nullable=False, default="programmable-adar-rna-editing")
    targeted_adenosine_to_inosine_editing_efficiency_pct = Column(Float, nullable=False, default=78.4)
    bystander_adenosine_deamination_rate_pct = Column(Float, nullable=False, default=2.1)
    guide_circular_rna_stability_half_life_hours = Column(Float, nullable=False, default=48.0)
    target_transcript_restoration_fold = Column(Float, nullable=False, default=12.5)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("RnaTargetedAdarDeaminaseEditingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("RnaTargetedAdarDeaminaseEditingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class RnaTargetedAdarDeaminaseEditingItemProfile(Base):
    """Detailed item profile for Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

    __tablename__ = "p566_rna_targeted_adar_deaminase_editing_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p566_rna_targeted_adar_deaminase_editing_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RnaTargetedAdarDeaminaseEditingStudy", back_populates="item_profiles")


class RnaTargetedAdarDeaminaseEditingMetricTrace(Base):
    """Metric trace for Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

    __tablename__ = "p566_rna_targeted_adar_deaminase_editing_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p566_rna_targeted_adar_deaminase_editing_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RnaTargetedAdarDeaminaseEditingStudy", back_populates="metric_traces")
