"""SQLAlchemy models for Phase 473: Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class FlexoelectricMembraneCurvatureStudy(Base):
    """Study record for Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

    __tablename__ = "p473_flexoelectric_membrane_curvature_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Asymmetric Phospholipid Bilayer Giant Unilamellar Vesicle with Micropipette Aspiration Curvature")
    analytical_modality = Column(String(100), nullable=False, default="flexoelectric-membrane-curvature")
    flexoelectric_coupling_coefficient_pC_per_m = Column(Float, nullable=False, default=12.4)
    membrane_curvature_radius_nm = Column(Float, nullable=False, default=45.0)
    transmembrane_induced_polarization_potential_mV = Column(Float, nullable=False, default=28.5)
    lipid_dipole_reorientation_energy_kj_mol = Column(Float, nullable=False, default=3.42)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("FlexoelectricMembraneCurvatureItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("FlexoelectricMembraneCurvatureMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class FlexoelectricMembraneCurvatureItemProfile(Base):
    """Detailed item profile for Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

    __tablename__ = "p473_flexoelectric_membrane_curvature_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p473_flexoelectric_membrane_curvature_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("FlexoelectricMembraneCurvatureStudy", back_populates="item_profiles")


class FlexoelectricMembraneCurvatureMetricTrace(Base):
    """Metric trace for Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

    __tablename__ = "p473_flexoelectric_membrane_curvature_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p473_flexoelectric_membrane_curvature_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("FlexoelectricMembraneCurvatureStudy", back_populates="metric_traces")
