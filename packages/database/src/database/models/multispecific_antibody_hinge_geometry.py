"""SQLAlchemy models for Phase 254: Autonomous Multi-Specific Antibody Fragment Geometry & Hinge Flexibility In-Silico Modeling Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MultispecificAntibodyHingeGeometryStudy(Base):
    """Study record for Simulates multi-specific antibody Fab-Fc inter-domain angles, hinge torsional potentials, and steric compatibility for simultaneous dual-epitope target binding.."""

    __tablename__ = "ms_ab_hinge_geom_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="multispecific-antibody-hinge-geometry")
    simultaneous_dual_binding_efficiency_pct = Column(Float, nullable=False, default=97.5)
    hinge_flexibility_rmsf_angstrom = Column(Float, nullable=False, default=4.8)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MultispecificAntibodyHingeGeometryItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("MultispecificAntibodyHingeGeometryMetricTrace", back_populates="study", cascade="all, delete-orphan")


class MultispecificAntibodyHingeGeometryItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "ms_ab_hinge_geom_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("ms_ab_hinge_geom_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MultispecificAntibodyHingeGeometryStudy", back_populates="item_profiles")


class MultispecificAntibodyHingeGeometryMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "ms_ab_hinge_geom_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("ms_ab_hinge_geom_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MultispecificAntibodyHingeGeometryStudy", back_populates="metric_traces")
