"""
Phase 110: Clinical-Genomic Survival Prognosis & Multi-Omics Stratification Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSON

class DBMultiOmicsPrognosticModel(Base):
    __tablename__ = "survival_prognostic_models"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    model_name = Column(String(200), nullable=False)
    cancer_cohort = Column(String(100), nullable=False, default="TCGA-LUAD")
    c_index_score = Column(Float, nullable=False, default=0.82)
    hazard_ratio_high_vs_low = Column(Float, nullable=False, default=3.45)
    log_rank_p_value = Column(Float, nullable=False, default=0.0001)
    risk_stratification_method = Column(String(100), nullable=False, default="Cox-Proportional-Hazards")
    features_weights = Column(JSON, nullable=False) # {gene/marker: beta_weight}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patients = relationship("DBSurvivalCohortPatient", back_populates="model", cascade="all, delete-orphan")
    curves = relationship("DBSurvivalStratificationCurve", back_populates="model", cascade="all, delete-orphan")


class DBSurvivalCohortPatient(Base):
    __tablename__ = "survival_cohort_patients"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID(), ForeignKey("survival_prognostic_models.id", ondelete="CASCADE"), nullable=False)
    patient_barcode = Column(String(100), nullable=False)
    overall_survival_months = Column(Float, nullable=False)
    vital_status = Column(Integer, nullable=False, default=0) # 0=censored/alive, 1=event/deceased
    risk_group = Column(String(50), nullable=False)           # HIGH, INTERMEDIATE, LOW
    risk_score = Column(Float, nullable=False)
    biomarker_vector = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("DBMultiOmicsPrognosticModel", back_populates="patients")


class DBSurvivalStratificationCurve(Base):
    __tablename__ = "survival_stratification_curves"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID(), ForeignKey("survival_prognostic_models.id", ondelete="CASCADE"), nullable=False)
    risk_tier = Column(String(50), nullable=False) # HIGH, INTERMEDIATE, LOW
    time_points_months = Column(JSON, nullable=False) # [0, 6, 12, 24, 36, 48, 60]
    survival_probability_km = Column(JSON, nullable=False) # [1.0, 0.85, 0.72, ...]
    patients_at_risk = Column(JSON, nullable=False) # [50, 42, 35, ...]
    median_survival_months = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("DBMultiOmicsPrognosticModel", back_populates="curves")
