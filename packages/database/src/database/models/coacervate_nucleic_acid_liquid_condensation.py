"""SQLAlchemy models for Phase 527: Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CoacervateNucleicAcidLiquidCondensationStudy(Base):
    """Study record for Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

    __tablename__ = "p527_coacervate_nucleic_acid_liquid_condensation_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Polycationic Polylysine-Spermidine Complex Coacervate Droplet Encapsulating Hammerhead Ribozymes")
    analytical_modality = Column(String(100), nullable=False, default="coacervate-rna-condensation")
    ribozyme_cleavage_rate_enhancement_fold = Column(Float, nullable=False, default=48.0)
    partition_coefficient_k_partition = Column(Float, nullable=False, default=125.0)
    droplet_interfacial_surface_tension_uN_m = Column(Float, nullable=False, default=0.85)
    critical_coacervation_transition_temp_c = Column(Float, nullable=False, default=37.2)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CoacervateNucleicAcidLiquidCondensationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CoacervateNucleicAcidLiquidCondensationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CoacervateNucleicAcidLiquidCondensationItemProfile(Base):
    """Detailed item profile for Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

    __tablename__ = "p527_coacervate_nucleic_acid_liquid_condensation_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p527_coacervate_nucleic_acid_liquid_condensation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CoacervateNucleicAcidLiquidCondensationStudy", back_populates="item_profiles")


class CoacervateNucleicAcidLiquidCondensationMetricTrace(Base):
    """Metric trace for Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

    __tablename__ = "p527_coacervate_nucleic_acid_liquid_condensation_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p527_coacervate_nucleic_acid_liquid_condensation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CoacervateNucleicAcidLiquidCondensationStudy", back_populates="metric_traces")
