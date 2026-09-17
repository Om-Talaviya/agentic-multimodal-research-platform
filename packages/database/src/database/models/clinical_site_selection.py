"""Clinical Trial Site Selection & Protocol Feasibility Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBTrialSiteStudy(Base):
    """Clinical Trial Study definition for site selection and protocol feasibility."""
    __tablename__ = "trial_site_studies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_title = Column(String(255), nullable=False)
    protocol_code = Column(String(64), nullable=False, index=True)
    indication = Column(String(128), nullable=False)
    phase = Column(String(32), nullable=False)  # Phase 1, Phase 2, Phase 3, Phase 4
    target_enrollment = Column(Integer, nullable=False, default=100)
    recruitment_duration_months = Column(Float, nullable=False, default=12.0)
    total_sites = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sites = relationship("DBCandidateTrialSite", back_populates="study", cascade="all, delete-orphan")
    simulations = relationship("DBRecruitmentSimulation", back_populates="study", cascade="all, delete-orphan")


class DBCandidateTrialSite(Base):
    """Candidate clinical trial site with recruitment velocity and compliance metrics."""
    __tablename__ = "candidate_trial_sites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String(36), ForeignKey("trial_site_studies.id", ondelete="CASCADE"), nullable=False)
    site_name = Column(String(255), nullable=False)
    country = Column(String(64), nullable=False)
    city = Column(String(128), nullable=False)
    principal_investigator = Column(String(128), nullable=False)
    historical_recruitment_rate = Column(Float, nullable=False, default=1.0)  # patients/month
    ethics_approval_timeline_days = Column(Integer, nullable=False, default=45)
    patient_pool_density = Column(Integer, nullable=False, default=1000)
    feasibility_score = Column(Float, nullable=False, default=0.5)  # 0.0 - 1.0
    risk_tier = Column(String(32), nullable=False, default="LOW_RISK")  # LOW_RISK, MODERATE_RISK, HIGH_RISK
    selected_for_trial = Column(Boolean, default=True)
    metrics_json = Column(JSON, default=dict)

    study = relationship("DBTrialSiteStudy", back_populates="sites")


class DBRecruitmentSimulation(Base):
    """Recruitment timeline forecasting simulation (Monte Carlo / Poisson)."""
    __tablename__ = "recruitment_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String(36), ForeignKey("trial_site_studies.id", ondelete="CASCADE"), nullable=False)
    simulation_name = Column(String(128), nullable=False)
    target_timeline_months = Column(Float, nullable=False)
    p10_completion_months = Column(Float, nullable=False)
    p50_completion_months = Column(Float, nullable=False)
    p90_completion_months = Column(Float, nullable=False)
    dropout_rate = Column(Float, nullable=False, default=0.10)
    enrollment_curve_json = Column(JSON, default=list)
    bottleneck_risks_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    study = relationship("DBTrialSiteStudy", back_populates="simulations")
