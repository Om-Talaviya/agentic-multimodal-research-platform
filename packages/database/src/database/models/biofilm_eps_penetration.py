"""SQLAlchemy models for Phase 357: Autonomous Bacterial Biofilm Extracellular Polymeric Substance (EPS) Disruption & Penetration Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BiofilmEpsPenetrationStudy(Base):
    """Study record for Models viscoelastic exopolysaccharide (alginate, Pel, Psl) matrix degradation by enzyme-loaded catalytic nanoparticles to reverse multi-drug tolerant antimicrobial persister cell dormancy.."""

    __tablename__ = "p357_biofilm_eps_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="biofilm-eps-penetration")
    biofilm_biomass_eradication_efficiency_pct = Column(Float, nullable=False, default=96.5)
    antimicrobial_diffusive_penetration_rate_um_min = Column(Float, nullable=False, default=42.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BiofilmEpsPenetrationItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("BiofilmEpsPenetrationMetricTrace", back_populates="study", cascade="all, delete-orphan")


class BiofilmEpsPenetrationItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p357_biofilm_eps_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p357_biofilm_eps_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BiofilmEpsPenetrationStudy", back_populates="item_profiles")


class BiofilmEpsPenetrationMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p357_biofilm_eps_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p357_biofilm_eps_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BiofilmEpsPenetrationStudy", back_populates="metric_traces")
