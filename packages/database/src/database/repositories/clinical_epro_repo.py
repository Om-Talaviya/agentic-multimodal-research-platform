"""Repository for Clinical Trial ePRO (Phase 141)."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.clinical_epro import (
    DBePROClinicalTrialStudy,
    DBPatientSurveyTelemetry,
    DBePROAdverseEventAlert,
)


class ClinicalePRORepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        protocol_id: str,
        therapeutic_area: str,
        patient_count: int,
        compliance_rate: float,
        composite_qol_score: float,
    ) -> DBePROClinicalTrialStudy:
        study = DBePROClinicalTrialStudy(
            protocol_id=protocol_id,
            therapeutic_area=therapeutic_area,
            patient_count=patient_count,
            compliance_rate=compliance_rate,
            composite_qol_score=composite_qol_score,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_survey_telemetry(
        self,
        study_id: uuid.UUID,
        patient_pseudonym: str,
        visit_day: int,
        vas_pain_score: float,
        promis_fatigue_score: float,
        eq5d_utility_index: float,
    ) -> DBPatientSurveyTelemetry:
        t = DBPatientSurveyTelemetry(
            study_id=study_id,
            patient_pseudonym=patient_pseudonym,
            visit_day=visit_day,
            vas_pain_score=vas_pain_score,
            promis_fatigue_score=promis_fatigue_score,
            eq5d_utility_index=eq5d_utility_index,
        )
        self.db.add(t)
        await self.db.commit()
        await self.db.refresh(t)
        return t

    async def add_adverse_event_alert(
        self,
        study_id: uuid.UUID,
        patient_pseudonym: str,
        ctcae_grade: int,
        symptom_name: str,
        requires_site_escalation: bool,
    ) -> DBePROAdverseEventAlert:
        ae = DBePROAdverseEventAlert(
            study_id=study_id,
            patient_pseudonym=patient_pseudonym,
            ctcae_grade=ctcae_grade,
            symptom_name=symptom_name,
            requires_site_escalation=requires_site_escalation,
        )
        self.db.add(ae)
        await self.db.commit()
        await self.db.refresh(ae)
        return ae

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBePROClinicalTrialStudy]:
        stmt = (
            select(DBePROClinicalTrialStudy)
            .where(DBePROClinicalTrialStudy.id == study_id)
            .options(
                selectinload(DBePROClinicalTrialStudy.surveys),
                selectinload(DBePROClinicalTrialStudy.adverse_events),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
