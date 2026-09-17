"""Pharmacovigilance Real-World Safety Signal Mining Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBPharmacovigilanceStudy(Base):
    """Pharmacovigilance study record for spontaneous reporting signal detection."""
    __tablename__ = "pv_sentinel_studies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_name = Column(String(255), nullable=False)
    drug_name = Column(String(128), nullable=False, index=True)
    active_substance = Column(String(128), nullable=False)
    target_adverse_event = Column(String(128), nullable=False, index=True)
    data_source = Column(String(64), nullable=False, default="FAERS")  # FAERS, VIGIBASE, EHR_RWE
    total_cases_analyzed = Column(Integer, nullable=False, default=1000)
    signal_status = Column(String(32), nullable=False)  # CONFIRMED_SIGNAL, POTENTIAL_SIGNAL, NO_SIGNAL
    who_causality_grade = Column(String(32), nullable=False, default="PROBABLE")
    study_summary_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    metrics = relationship("DBSignalDisproportionality", back_populates="study", cascade="all, delete-orphan")
    case_reports = relationship("DBAdverseEventCaseReport", back_populates="study", cascade="all, delete-orphan")


class DBSignalDisproportionality(Base):
    """Statistical disproportionality metrics (PRR, ROR, IC025, EBGM)."""
    __tablename__ = "pv_disproportionality_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String(36), ForeignKey("pv_sentinel_studies.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String(32), nullable=False)  # PRR, ROR, IC025, EBGM, CHI_SQUARE
    value = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float, nullable=False)
    confidence_interval_upper = Column(Float, nullable=False)
    is_statistically_significant = Column(Boolean, default=False)
    threshold_exceeded = Column(Boolean, default=False)

    study = relationship("DBPharmacovigilanceStudy", back_populates="metrics")


class DBAdverseEventCaseReport(Base):
    """De-identified spontaneous case report from FAERS/EHR."""
    __tablename__ = "pv_adverse_event_cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String(36), ForeignKey("pv_sentinel_studies.id", ondelete="CASCADE"), nullable=False)
    report_id = Column(String(64), nullable=False)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String(16), nullable=False, default="Unknown")
    primary_suspect_drug = Column(String(128), nullable=False)
    concomitant_drugs_json = Column(JSON, default=list)
    adverse_event_term = Column(String(128), nullable=False)
    meddra_soc = Column(String(128), nullable=False)  # System Organ Class
    time_to_onset_days = Column(Integer, nullable=True)
    outcome = Column(String(64), nullable=False, default="RECOVERED")  # RECOVERED, HOSPITALIZATION, LIFE_THREATENING, DEATH

    study = relationship("DBPharmacovigilanceStudy", back_populates="case_reports")
