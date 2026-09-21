"""Trial Telemetry Models (Phase 122)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBTrialSubjectTelemetryCohort(Base):
    __tablename__ = "telemetry_cohorts"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    protocol_number = Column(String(100), nullable=False)
    total_active_subjects = Column(Integer, default=150, nullable=False)
    telemetry_frequency_hz = Column(Float, default=1.0, nullable=False)
    anomaly_alert_threshold = Column(Float, default=0.92, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    anomalies = relationship("DBDigitalBiomarkerAnomaly", back_populates="cohort", cascade="all, delete-orphan")

class DBDigitalBiomarkerAnomaly(Base):
    __tablename__ = "telemetry_anomalies"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    cohort_id = Column(GUID(), ForeignKey("telemetry_cohorts.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(100), nullable=False)
    biomarker_stream_type = Column(String(100), nullable=False)
    anomaly_severity_score = Column(Float, nullable=False)
    ecog_performance_delta = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cohort = relationship("DBTrialSubjectTelemetryCohort", back_populates="anomalies")
