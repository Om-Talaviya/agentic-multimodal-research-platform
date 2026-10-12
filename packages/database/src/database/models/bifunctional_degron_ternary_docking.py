"""SQLAlchemy models for Phase 430: Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BifunctionalDegronTernaryDockingStudy(Base):
    """Study record for Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster."""

    __tablename__ = "p430_bifunctional_degron_ternary_docking_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="VHL-E3 Ligase, Linker, and Target Oncogenic Kinase Complex")
    analytical_modality = Column(String(100), nullable=False, default="bifunctional-degron-docking")
    ternary_complex_cooperativity_alpha = Column(Float, nullable=False, default=3.42)
    buried_solvent_accessible_surface_angstrom2 = Column(Float, nullable=False, default=1140.0)
    ubiquitination_zone_distance_angstrom = Column(Float, nullable=False, default=12.8)
    hook_effect_concentration_uM = Column(Float, nullable=False, default=2.5)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BifunctionalDegronTernaryDockingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BifunctionalDegronTernaryDockingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BifunctionalDegronTernaryDockingItemProfile(Base):
    """Detailed item profile for Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster."""

    __tablename__ = "p430_bifunctional_degron_ternary_docking_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p430_bifunctional_degron_ternary_docking_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BifunctionalDegronTernaryDockingStudy", back_populates="item_profiles")


class BifunctionalDegronTernaryDockingMetricTrace(Base):
    """Metric trace for Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster."""

    __tablename__ = "p430_bifunctional_degron_ternary_docking_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p430_bifunctional_degron_ternary_docking_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BifunctionalDegronTernaryDockingStudy", back_populates="metric_traces")
