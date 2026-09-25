"""SQLAlchemy models for Phase 186: Multi-Parametric Oncology Radiomics & Habitat Imaging Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class RadiomicsDeepImagingStudy(Base):
    """Study record for multi-parametric CT/MRI/PET tumor habitat extraction and radiogenomic biomarker profiling."""

    __tablename__ = "radiomics_deep_imaging_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    scan_modality = Column(String(100), nullable=False, default="Multiparametric MRI (T1c, T2, FLAIR, DWI)")
    tumor_type = Column(String(100), nullable=False, default="Glioblastoma Multiforme")
    gross_tumor_volume_cm3 = Column(Float, nullable=False, default=48.5)
    necrotic_core_fraction = Column(Float, nullable=False, default=0.24)
    active_rim_fraction = Column(Float, nullable=False, default=0.46)
    edema_infiltrative_fraction = Column(Float, nullable=False, default=0.30)
    intratumoral_heterogeneity_index = Column(Float, nullable=False, default=0.89)
    predicted_overall_survival_months = Column(Float, nullable=False, default=18.4)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    habitat_subregions = relationship("RadiomicsHabitatSubregion", back_populates="study", cascade="all, delete-orphan")
    texture_features = relationship("RadiomicsExtractedTextureFeature", back_populates="study", cascade="all, delete-orphan")


class RadiomicsHabitatSubregion(Base):
    """Physiological tumor habitat subregion spatial boundaries."""

    __tablename__ = "radiomics_habitat_subregions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("radiomics_deep_imaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    subregion_name = Column(String(100), nullable=False)  # Hypervascular Rim, Hypoxic Core, Peritumoral Infiltrate
    volume_cm3 = Column(Float, nullable=False)
    mean_perfusion_ktrans = Column(Float, nullable=False)
    apparent_diffusion_coefficient_adc = Column(Float, nullable=False)
    hypoxia_pet_avidity_suv = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RadiomicsDeepImagingStudy", back_populates="habitat_subregions")


class RadiomicsExtractedTextureFeature(Base):
    """IBSI-compliant GLCM, GLRLM, GLSZM, and Wavelet texture features."""

    __tablename__ = "radiomics_extracted_texture_features"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("radiomics_deep_imaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_class = Column(String(100), nullable=False)  # GLCM, Shape3D, Wavelet-HHL, FirstOrder
    feature_name = Column(String(150), nullable=False)  # e.g., GLCM_Contrast, SurfaceToVolumeRatio
    feature_value = Column(Float, nullable=False)
    ibsi_compliance_flag = Column(Boolean, nullable=False, default=True)
    radiogenomic_weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RadiomicsDeepImagingStudy", back_populates="texture_features")