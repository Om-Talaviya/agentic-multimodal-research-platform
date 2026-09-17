"""Multi-Modal Biomarker Discovery & Multi-Omics Signature Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class DBBiomarkerDiscoveryStudy(Base):
    __tablename__ = "biomarker_discovery_studies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_title = Column(String(255), nullable=False)
    disease_indication = Column(String(255), nullable=False)
    cohort_sample_size = Column(Integer, default=100)
    omics_layers_json = Column(JSON, default=list)
    signature_stability_score = Column(Float, default=0.85)
    auc_roc_score = Column(Float, default=0.91)
    study_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    features = relationship("DBBiomarkerFeature", back_populates="study", cascade="all, delete-orphan")
    stratifications = relationship("DBPatientRiskStratification", back_populates="study", cascade="all, delete-orphan")


class DBBiomarkerFeature(Base):
    __tablename__ = "biomarker_features"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String(36), ForeignKey("biomarker_discovery_studies.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(255), nullable=False)
    omics_modality = Column(String(64), nullable=False)
    log2_fold_change = Column(Float, default=0.0)
    adjusted_p_value = Column(Float, default=0.05)
    feature_importance_weight = Column(Float, default=0.5)
    correlation_direction = Column(String(32), default="POSITIVE")

    study = relationship("DBBiomarkerDiscoveryStudy", back_populates="features")


class DBPatientRiskStratification(Base):
    __tablename__ = "biomarker_patient_stratifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String(36), ForeignKey("biomarker_discovery_studies.id", ondelete="CASCADE"), nullable=False)
    patient_cohort_id = Column(String(128), nullable=False)
    prognostic_risk_tier = Column(String(32), default="INTERMEDIATE")
    response_probability_score = Column(Float, default=0.5)
    composite_signature_score = Column(Float, default=0.0)
    signature_expression_map_json = Column(JSON, default=dict)

    study = relationship("DBBiomarkerDiscoveryStudy", back_populates="stratifications")
