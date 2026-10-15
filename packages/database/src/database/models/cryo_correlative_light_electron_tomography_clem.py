"""SQLAlchemy models for Phase 544: Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoCorrelativeLightElectronTomographyClemStudy(Base):
    """Study record for Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

    __tablename__ = "p544_cryo_correlative_light_electron_tomography_clem_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Cryo-Vitrified Neuronal Cultured Grid with Tetraspeck Fluorescent Nanobeads and Sub-10nm Gold Fiducials")
    analytical_modality = Column(String(100), nullable=False, default="cryo-clem-fiducial-correlation")
    cross_modality_3d_registration_precision_nm = Column(Float, nullable=False, default=12.2)
    cryo_fluorescence_signal_to_background_ratio = Column(Float, nullable=False, default=48.5)
    cryo_fib_milling_target_accuracy_nm = Column(Float, nullable=False, default=24.0)
    subtomogram_correlation_coefficient = Column(Float, nullable=False, default=0.925)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoCorrelativeLightElectronTomographyClemItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoCorrelativeLightElectronTomographyClemMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoCorrelativeLightElectronTomographyClemItemProfile(Base):
    """Detailed item profile for Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

    __tablename__ = "p544_cryo_correlative_light_electron_tomography_clem_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p544_cryo_correlative_light_electron_tomography_clem_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoCorrelativeLightElectronTomographyClemStudy", back_populates="item_profiles")


class CryoCorrelativeLightElectronTomographyClemMetricTrace(Base):
    """Metric trace for Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

    __tablename__ = "p544_cryo_correlative_light_electron_tomography_clem_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p544_cryo_correlative_light_electron_tomography_clem_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoCorrelativeLightElectronTomographyClemStudy", back_populates="metric_traces")
