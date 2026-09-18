"""Radiogenomics & 3D Volumetric Medical Imaging AI Feature Extraction Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base


class DBRadiogenomicsScan(Base):
    __tablename__ = "radiogenomics_scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(64), nullable=False)
    modality = Column(String(64), default="MRI_T1_CONTRAST")
    anatomical_region = Column(String(64), default="BRAIN_GLIOMA")
    voxel_spacing_mm = Column(String(32), default="1.0x1.0x1.0")
    lesion_volume_cm3 = Column(Float, default=24.5)
    segmentation_mask_status = Column(String(32), default="SEGMENTED")
    scan_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    radiomic_features = relationship("DBVolumetricRadiomicFeature", back_populates="scan", cascade="all, delete-orphan")
    genomic_correlations = relationship("DBImagingGenomicCorrelation", back_populates="scan", cascade="all, delete-orphan")


class DBVolumetricRadiomicFeature(Base):
    __tablename__ = "volumetric_radiomic_features"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("radiogenomics_scans.id", ondelete="CASCADE"), nullable=False)
    feature_family = Column(String(64), default="IBSI_SHAPE_3D")
    feature_name = Column(String(128), nullable=False)
    feature_value = Column(Float, default=0.785)
    normalized_z_score = Column(Float, default=1.24)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("DBRadiogenomicsScan", back_populates="radiomic_features")


class DBImagingGenomicCorrelation(Base):
    __tablename__ = "imaging_genomic_correlations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("radiogenomics_scans.id", ondelete="CASCADE"), nullable=False)
    predicted_genomic_alteration = Column(String(128), nullable=False)  # IDH1_R132H, EGFR_EXON19_DEL
    prediction_probability = Column(Float, default=0.912)
    feature_importance_json = Column(JSON, default=dict)
    clinical_significance = Column(String(255), default="High likelihood of favorable temozolomide response")
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("DBRadiogenomicsScan", back_populates="genomic_correlations")
