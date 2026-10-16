"""SQLAlchemy models for Phase 569: Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SuperResolutionCryoFluorescenceCorrelatorStudy(Base):
    """Study record for Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""

    __tablename__ = "p569_super_resolution_cryo_fluorescence_correlator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Mammalian HeLa Lamella with Cryo-Photoswitchable mEos4b Fluorophores and Gold Nanoparticle Fiducials")
    analytical_modality = Column(String(100), nullable=False, default="cryo-super-resolution-registration")
    fiducial_registration_precision_nm = Column(Float, nullable=False, default=4.8)
    photobleaching_threshold_flux_kw_cm2 = Column(Float, nullable=False, default=12.5)
    localization_confidence_score = Column(Float, nullable=False, default=0.985)
    cryo_optical_drift_variance_nm2 = Column(Float, nullable=False, default=1.25)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SuperResolutionCryoFluorescenceCorrelatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SuperResolutionCryoFluorescenceCorrelatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SuperResolutionCryoFluorescenceCorrelatorItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""

    __tablename__ = "p569_super_resolution_cryo_fluorescence_correlator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p569_super_resolution_cryo_fluorescence_correlator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SuperResolutionCryoFluorescenceCorrelatorStudy", back_populates="item_profiles")


class SuperResolutionCryoFluorescenceCorrelatorMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""

    __tablename__ = "p569_super_resolution_cryo_fluorescence_correlator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p569_super_resolution_cryo_fluorescence_correlator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SuperResolutionCryoFluorescenceCorrelatorStudy", back_populates="metric_traces")
