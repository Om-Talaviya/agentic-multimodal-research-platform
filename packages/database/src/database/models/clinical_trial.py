"""
Phase 46: Autonomous Clinical Trial Protocol Optimizer & Patient-Cohort Stratifier Models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer, JSON
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


class DBClinicalTrialProtocol(Base):
    __tablename__ = "clinical_trial_protocols"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    phase = Column(String(50), default="Phase II") # Phase I, Phase II, Phase III, Phase IV
    target_indication = Column(String(255), nullable=False)
    investigational_agent = Column(String(255), nullable=False)
    primary_endpoint = Column(String(500), nullable=False)
    sample_size_target = Column(Integer, default=120)
    statistical_power = Column(Float, default=0.85)
    estimated_duration_months = Column(Integer, default=18)
    status = Column(String(50), default="DRAFTED") # DRAFTED, OPTIMIZED, RECRUITING, COMPLETED
    protocol_summary = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONType, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eligibility_criteria = relationship("DBEligibilityCriterion", back_populates="protocol", cascade="all, delete-orphan")
    cohort_matches = relationship("DBCohortPatientMatch", back_populates="protocol", cascade="all, delete-orphan")
    synthetic_arms = relationship("DBSyntheticControlArm", back_populates="protocol", cascade="all, delete-orphan")


class DBEligibilityCriterion(Base):
    __tablename__ = "trial_eligibility_criteria"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID, ForeignKey("clinical_trial_protocols.id", ondelete="CASCADE"), nullable=False)
    criterion_type = Column(String(50), nullable=False) # INCLUSION, EXCLUSION
    category = Column(String(100), default="CLINICAL") # CLINICAL, BIOMARKER, DEMOGRAPHIC, PRIOR_THERAPY
    description = Column(Text, nullable=False)
    structured_rule = Column(JSONType, default=dict) # {"variable": "ECOG_PS", "op": "<=", "val": 1}
    impact_on_enrollment_rate = Column(Float, default=0.0) # -1.0 to 0.0
    created_at = Column(DateTime, default=datetime.utcnow)

    protocol = relationship("DBClinicalTrialProtocol", back_populates="eligibility_criteria")


class DBCohortPatientMatch(Base):
    __tablename__ = "trial_cohort_patient_matches"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID, ForeignKey("clinical_trial_protocols.id", ondelete="CASCADE"), nullable=False)
    patient_identifier = Column(String(100), nullable=False)
    phenotype_match_score = Column(Float, default=0.0) # 0.0 to 1.0
    biomarker_alignment = Column(String(100), default="OPTIMAL") # OPTIMAL, PARTIAL, MISMATCH
    eligibility_verdict = Column(String(50), default="ELIGIBLE") # ELIGIBLE, INELIGIBLE, CONDITIONAL
    exclusion_flags = Column(JSONType, default=list)
    survival_estimate_months = Column(Float, default=14.5)
    hazard_ratio = Column(Float, default=0.68)
    created_at = Column(DateTime, default=datetime.utcnow)

    protocol = relationship("DBClinicalTrialProtocol", back_populates="cohort_matches")


class DBSyntheticControlArm(Base):
    __tablename__ = "trial_synthetic_control_arms"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID, ForeignKey("clinical_trial_protocols.id", ondelete="CASCADE"), nullable=False)
    rwe_data_source = Column(String(255), default="EHR Flatiron/SEER Database")
    baseline_patient_count = Column(Integer, default=500)
    matched_patient_count = Column(Integer, default=120)
    propensity_score_caliper = Column(Float, default=0.05)
    median_overall_survival_control_months = Column(Float, default=9.2)
    median_overall_survival_interventional_months = Column(Float, default=16.8)
    p_value_log_rank = Column(Float, default=0.0012)
    hazard_ratio = Column(Float, default=0.55)
    survival_curve_data = Column(JSONType, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    protocol = relationship("DBClinicalTrialProtocol", back_populates="synthetic_arms")
