"""SQLAlchemy models for Phase 464: Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SymbioticConsortiaDivisionOfLaborStudy(Base):
    """Study record for Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

    __tablename__ = "p464_symbiotic_consortia_division_of_labor_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered E. coli and S. cerevisiae Cross-Feeding Co-Culture in Chemostat Bioreactor")
    analytical_modality = Column(String(100), nullable=False, default="symbiotic-metabolic-labor-dynamics")
    chemostat_steady_state_biomass_ratio = Column(Float, nullable=False, default=1.15)
    cross_feeding_metabolite_exchange_flux_mmol_g_hr = Column(Float, nullable=False, default=6.85)
    population_coexistence_lyapunov_exponent = Column(Float, nullable=False, default=-0.42)
    resource_utilization_synergy_factor = Column(Float, nullable=False, default=1.85)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SymbioticConsortiaDivisionOfLaborItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SymbioticConsortiaDivisionOfLaborMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SymbioticConsortiaDivisionOfLaborItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

    __tablename__ = "p464_symbiotic_consortia_division_of_labor_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p464_symbiotic_consortia_division_of_labor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SymbioticConsortiaDivisionOfLaborStudy", back_populates="item_profiles")


class SymbioticConsortiaDivisionOfLaborMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

    __tablename__ = "p464_symbiotic_consortia_division_of_labor_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p464_symbiotic_consortia_division_of_labor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SymbioticConsortiaDivisionOfLaborStudy", back_populates="metric_traces")
