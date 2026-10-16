"""SQLAlchemy models for Phase 549: Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ActiveChiralHydrodynamicsVorticityStudy(Base):
    """Study record for Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

    __tablename__ = "p549_active_chiral_hydrodynamics_vorticity_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Chiral Rotating Flagellated Micro-Swarm Escherichia coli in Confined Annular Microfluidic Cavities")
    analytical_modality = Column(String(100), nullable=False, default="active-chiral-hydrodynamics")
    swarming_vorticity_enstrophy_density_s2 = Column(Float, nullable=False, default=145.2)
    chiral_odd_viscosity_coefficient_pa_s = Column(Float, nullable=False, default=0.082)
    collective_topological_circulation_rate_rad_s = Column(Float, nullable=False, default=18.4)
    microfluidic_boundary_shear_stress_pa = Column(Float, nullable=False, default=0.36)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("ActiveChiralHydrodynamicsVorticityItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("ActiveChiralHydrodynamicsVorticityMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class ActiveChiralHydrodynamicsVorticityItemProfile(Base):
    """Detailed item profile for Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

    __tablename__ = "p549_active_chiral_hydrodynamics_vorticity_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p549_active_chiral_hydrodynamics_vorticity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ActiveChiralHydrodynamicsVorticityStudy", back_populates="item_profiles")


class ActiveChiralHydrodynamicsVorticityMetricTrace(Base):
    """Metric trace for Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

    __tablename__ = "p549_active_chiral_hydrodynamics_vorticity_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p549_active_chiral_hydrodynamics_vorticity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ActiveChiralHydrodynamicsVorticityStudy", back_populates="metric_traces")
