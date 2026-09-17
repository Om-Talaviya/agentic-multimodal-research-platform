"""Repository for Pharmacovigilance Real-World Safety Signal Mining."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.pv_signal_mining import (
    DBPharmacovigilanceStudy,
    DBSignalDisproportionality,
    DBAdverseEventCaseReport,
)


class PVSignalMiningRepository:
    """Handles async database operations for pharmacovigilance safety signal detection."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        study_name: str,
        drug_name: str,
        active_substance: str,
        target_adverse_event: str,
        data_source: str = "FAERS",
        total_cases_analyzed: int = 1000,
        signal_status: str = "NO_SIGNAL",
        who_causality_grade: str = "PROBABLE",
        study_summary_json: Optional[Dict[str, Any]] = None,
    ) -> DBPharmacovigilanceStudy:
        study = DBPharmacovigilanceStudy(
            study_name=study_name,
            drug_name=drug_name,
            active_substance=active_substance,
            target_adverse_event=target_adverse_event,
            data_source=data_source,
            total_cases_analyzed=total_cases_analyzed,
            signal_status=signal_status,
            who_causality_grade=who_causality_grade,
            study_summary_json=study_summary_json or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: str) -> Optional[DBPharmacovigilanceStudy]:
        stmt = select(DBPharmacovigilanceStudy).where(DBPharmacovigilanceStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBPharmacovigilanceStudy]:
        stmt = select(DBPharmacovigilanceStudy).order_by(desc(DBPharmacovigilanceStudy.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_metrics(
        self,
        study_id: str,
        metrics_data: List[Dict[str, Any]],
    ) -> List[DBSignalDisproportionality]:
        created = []
        for m in metrics_data:
            item = DBSignalDisproportionality(
                study_id=study_id,
                metric_name=m["metric_name"],
                value=m["value"],
                confidence_interval_lower=m["confidence_interval_lower"],
                confidence_interval_upper=m["confidence_interval_upper"],
                is_statistically_significant=m.get("is_statistically_significant", False),
                threshold_exceeded=m.get("threshold_exceeded", False),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_metrics_by_study(self, study_id: str) -> List[DBSignalDisproportionality]:
        stmt = select(DBSignalDisproportionality).where(DBSignalDisproportionality.study_id == study_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_case_reports(
        self,
        study_id: str,
        cases_data: List[Dict[str, Any]],
    ) -> List[DBAdverseEventCaseReport]:
        created = []
        for c in cases_data:
            item = DBAdverseEventCaseReport(
                study_id=study_id,
                report_id=c["report_id"],
                patient_age=c.get("patient_age"),
                patient_gender=c.get("patient_gender", "Unknown"),
                primary_suspect_drug=c["primary_suspect_drug"],
                concomitant_drugs_json=c.get("concomitant_drugs_json", []),
                adverse_event_term=c["adverse_event_term"],
                meddra_soc=c.get("meddra_soc", "General Disorders"),
                time_to_onset_days=c.get("time_to_onset_days"),
                outcome=c.get("outcome", "RECOVERED"),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_cases_by_study(self, study_id: str) -> List[DBAdverseEventCaseReport]:
        stmt = select(DBAdverseEventCaseReport).where(DBAdverseEventCaseReport.study_id == study_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
