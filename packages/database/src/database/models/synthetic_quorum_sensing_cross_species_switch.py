"""SQLAlchemy models for Phase 513: Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticQuorumSensingCrossSpeciesSwitchStudy(Base):
    """Study record for Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

    __tablename__ = "p513_synthetic_quorum_sensing_cross_species_switch_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Co-Cultured Synthetic E. coli and B. subtilis Biofilm with AI-2 / CAI-1 Inter-Species Relays")
    analytical_modality = Column(String(100), nullable=False, default="cross-species-quorum-switch")
    interbacterial_signal_induction_threshold_nM = Column(Float, nullable=False, default=85.0)
    population_ratio_homeostasis_cv = Column(Float, nullable=False, default=0.042)
    cross_repression_bistable_switch_delay_min = Column(Float, nullable=False, default=18.5)
    metabolic_cross_feeding_syntrophy_rate_mM_per_hr = Column(Float, nullable=False, default=3.2)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticQuorumSensingCrossSpeciesSwitchItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SyntheticQuorumSensingCrossSpeciesSwitchMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SyntheticQuorumSensingCrossSpeciesSwitchItemProfile(Base):
    """Detailed item profile for Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

    __tablename__ = "p513_synthetic_quorum_sensing_cross_species_switch_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p513_synthetic_quorum_sensing_cross_species_switch_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticQuorumSensingCrossSpeciesSwitchStudy", back_populates="item_profiles")


class SyntheticQuorumSensingCrossSpeciesSwitchMetricTrace(Base):
    """Metric trace for Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

    __tablename__ = "p513_synthetic_quorum_sensing_cross_species_switch_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p513_synthetic_quorum_sensing_cross_species_switch_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticQuorumSensingCrossSpeciesSwitchStudy", back_populates="metric_traces")
