"""Clinical Trial Decentralized ePRO & Patient Reported Outcomes Models (Phase 141)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBePROClinicalTrialStudy(Base):
    """Decentralized clinical trial ePRO study protocol."""

    __tablename__ = "epro_clinical_trial_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(String(100), nullable=False)
    therapeutic_area = Column(String(100), nullable=False)
    patient_count = Column(Integer, default=0, nullable=False)
    compliance_rate = Column(Float, default=0.0)
    composite_qol_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    surveys = relationship("DBPatientSurveyTelemetry", back_populates="study", cascade="all, delete-orphan")
    adverse_events = relationship("DBePROAdverseEventAlert", back_populates="study", cascade="all, delete-orphan")


class DBPatientSurveyTelemetry(Base):
    """Patient questionnaire telemetry timepoint."""

    __tablename__ = "epro_patient_survey_telemetry"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("epro_clinical_trial_studies.id", ondelete="CASCADE"), nullable=False)
    patient_pseudonym = Column(String(100), nullable=False)
    visit_day = Column(Integer, nullable=False)
    vas_pain_score = Column(Float, nullable=False)
    promis_fatigue_score = Column(Float, nullable=False)
    eq5d_utility_index = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBePROClinicalTrialStudy", back_populates="surveys")


class DBePROAdverseEventAlert(Base):
    """Automated symptom worsening alert."""

    __tablename__ = "epro_adverse_event_alerts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("epro_clinical_trial_studies.id", ondelete="CASCADE"), nullable=False)
    patient_pseudonym = Column(String(100), nullable=False)
    ctcae_grade = Column(Integer, nullable=False)
    symptom_name = Column(String(100), nullable=False)
    requires_site_escalation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBePROClinicalTrialStudy", back_populates="adverse_events")
