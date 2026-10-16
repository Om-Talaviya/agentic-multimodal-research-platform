"""SQLAlchemy models for Phase 548: Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoElectronPtychographyReconstructionStudy(Base):
    """Study record for Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine."""

    __tablename__ = "p548_cryo_electron_ptychography_reconstruction_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Intact Vitrified Chlamydomonas reinhardtii Chloroplast Membrane Thylakoid with Fast Direct Electron Camera 4D-STEM")
    analytical_modality = Column(String(100), nullable=False, default="cryo-ptychography-4d-stem")
    sub_angstrom_phase_contrast_resolution_a = Column(Float, nullable=False, default=1.82)
    inelastic_mean_free_path_depth_nm = Column(Float, nullable=False, default=240.0)
    dose_efficiency_snr_gain_factor = Column(Float, nullable=False, default=5.8)
    phase_plate_wavefront_aberration_mrad = Column(Float, nullable=False, default=0.45)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoElectronPtychographyReconstructionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoElectronPtychographyReconstructionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoElectronPtychographyReconstructionItemProfile(Base):
    """Detailed item profile for Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine."""

    __tablename__ = "p548_cryo_electron_ptychography_reconstruction_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p548_cryo_electron_ptychography_reconstruction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoElectronPtychographyReconstructionStudy", back_populates="item_profiles")


class CryoElectronPtychographyReconstructionMetricTrace(Base):
    """Metric trace for Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine."""

    __tablename__ = "p548_cryo_electron_ptychography_reconstruction_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p548_cryo_electron_ptychography_reconstruction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoElectronPtychographyReconstructionStudy", back_populates="metric_traces")
