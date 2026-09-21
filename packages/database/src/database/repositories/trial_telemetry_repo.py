"""Trial Telemetry Repo (Phase 122)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.trial_telemetry import DBTrialSubjectTelemetryCohort, DBDigitalBiomarkerAnomaly

class TrialTelemetryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_cohort(self, workspace_id: uuid.UUID, protocol_number: str,
                            total_active_subjects: int, telemetry_frequency_hz: float,
                            anomaly_alert_threshold: float) -> DBTrialSubjectTelemetryCohort:
        c = DBTrialSubjectTelemetryCohort(
            workspace_id=workspace_id,
            protocol_number=protocol_number,
            total_active_subjects=total_active_subjects,
            telemetry_frequency_hz=telemetry_frequency_hz,
            anomaly_alert_threshold=anomaly_alert_threshold,
        )
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def add_anomaly(self, cohort_id: uuid.UUID, subject_id: str,
                          biomarker_stream_type: str, anomaly_severity_score: float,
                          ecog_performance_delta: float) -> DBDigitalBiomarkerAnomaly:
        a = DBDigitalBiomarkerAnomaly(
            cohort_id=cohort_id,
            subject_id=subject_id,
            biomarker_stream_type=biomarker_stream_type,
            anomaly_severity_score=anomaly_severity_score,
            ecog_performance_delta=ecog_performance_delta,
        )
        self.db.add(a)
        await self.db.commit()
        await self.db.refresh(a)
        return a

    async def get_cohort(self, cohort_id: uuid.UUID) -> Optional[DBTrialSubjectTelemetryCohort]:
        res = await self.db.execute(select(DBTrialSubjectTelemetryCohort).where(DBTrialSubjectTelemetryCohort.id == cohort_id))
        return res.scalar_one_or_none()
