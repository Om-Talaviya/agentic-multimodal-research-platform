"""SQLAlchemy models for Phase 433: Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SynchrotronSaxsEnsembleFitterStudy(Base):
    """Study record for Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

    __tablename__ = "p433_synchrotron_saxs_ensemble_fitter_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Intrinsically Disordered Kinase Domain in Solution")
    analytical_modality = Column(String(100), nullable=False, default="synchrotron-saxs")
    radius_of_gyration_Rg_angstrom = Column(Float, nullable=False, default=34.2)
    kratky_plot_flexibility_index = Column(Float, nullable=False, default=0.895)
    ensemble_fit_chi_squared = Column(Float, nullable=False, default=1.08)
    maximum_particle_dimension_Dmax_angstrom = Column(Float, nullable=False, default=112.0)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SynchrotronSaxsEnsembleFitterItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SynchrotronSaxsEnsembleFitterMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SynchrotronSaxsEnsembleFitterItemProfile(Base):
    """Detailed item profile for Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

    __tablename__ = "p433_synchrotron_saxs_ensemble_fitter_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p433_synchrotron_saxs_ensemble_fitter_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SynchrotronSaxsEnsembleFitterStudy", back_populates="item_profiles")


class SynchrotronSaxsEnsembleFitterMetricTrace(Base):
    """Metric trace for Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

    __tablename__ = "p433_synchrotron_saxs_ensemble_fitter_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p433_synchrotron_saxs_ensemble_fitter_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SynchrotronSaxsEnsembleFitterStudy", back_populates="metric_traces")
