"""Clinical Genomics Digital Twin & Patient Pharmacogenomics Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBPatientGenomicProfile(Base):
    __tablename__ = "patient_genomic_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_mrn = Column(String(64), nullable=False, unique=True)
    age = Column(Integer, default=58)
    sex = Column(String(16), default="FEMALE")
    ancestry = Column(String(64), default="EUROPEAN")
    total_star_alleles_called = Column(Integer, default=6)
    high_risk_drug_interactions_count = Column(Integer, default=2)
    clinical_notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    guidelines = relationship("DBPharmacogenomicGuideline", back_populates="profile", cascade="all, delete-orphan")
    twin_simulations = relationship("DBPatientDigitalTwinSim", back_populates="profile", cascade="all, delete-orphan")


class DBPharmacogenomicGuideline(Base):
    __tablename__ = "pharmacogenomic_guidelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("patient_genomic_profiles.id", ondelete="CASCADE"), nullable=False)
    gene_symbol = Column(String(32), nullable=False)  # CYP2D6, CYP2C19, etc.
    diplotype_call = Column(String(32), nullable=False)  # *1/*4, *2/*2
    metabolizer_phenotype = Column(String(64), default="INTERMEDIATE_METABOLIZER")
    affected_drug_class = Column(String(128), default="ANTIPLATELET_PRODRUGS")
    cpic_level = Column(String(16), default="LEVEL_A")
    clinical_dose_recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("DBPatientGenomicProfile", back_populates="guidelines")


class DBPatientDigitalTwinSim(Base):
    __tablename__ = "patient_digital_twin_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("patient_genomic_profiles.id", ondelete="CASCADE"), nullable=False)
    drug_administered = Column(String(128), nullable=False)  # Clopidogrel, Warfarin, etc.
    prescribed_dose_mg = Column(Float, default=75.0)
    predicted_auc_ratio = Column(Float, default=0.35)
    toxic_accumulation_risk = Column(String(32), default="LOW")
    recommended_adjusted_dose_mg = Column(Float, default=0.0)  # 0.0 indicates switch drug
    alternate_drug_suggestion = Column(String(128), default="Prasugrel or Ticagrelor")
    efficacy_score = Column(Float, default=0.92)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("DBPatientGenomicProfile", back_populates="twin_simulations")
