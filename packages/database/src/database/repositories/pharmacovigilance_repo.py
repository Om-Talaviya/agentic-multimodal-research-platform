"""
Repository for Pharmacovigilance Safety Signals & Disproportionality Metrics.
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.pharmacovigilance import (
    DBPharmacovigilanceCorpus,
    DBSafetySignalReport,
    DBDisproportionalityMetric
)

class PharmacovigilanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_corpus(
        self,
        title: str,
        data_sources: Optional[List[str]] = None,
        total_reports: int = 1250000,
        user_id: Optional[uuid.UUID] = None
    ) -> DBPharmacovigilanceCorpus:
        corpus = DBPharmacovigilanceCorpus(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            data_sources=data_sources or ["FDA_FAERS", "EudraVigilance"],
            total_adverse_reports=total_reports,
            status="ANALYZED"
        )
        self.session.add(corpus)
        await self.session.commit()
        await self.session.refresh(corpus)
        return corpus

    async def get_corpus(self, corpus_id: uuid.UUID) -> Optional[DBPharmacovigilanceCorpus]:
        query = (
            select(DBPharmacovigilanceCorpus)
            .options(
                selectinload(DBPharmacovigilanceCorpus.signals).selectinload(DBSafetySignalReport.metrics)
            )
            .where(DBPharmacovigilanceCorpus.id == corpus_id)
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_corpora(self, limit: int = 50) -> List[DBPharmacovigilanceCorpus]:
        query = select(DBPharmacovigilanceCorpus).order_by(DBPharmacovigilanceCorpus.created_at.desc()).limit(limit)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_signal(
        self,
        corpus_id: uuid.UUID,
        drug_name: str,
        adverse_reaction_term: str,
        system_organ_class: str,
        case_count: int,
        signal_priority: str,
        who_umc_causality: str,
        clinical_summary: Optional[str] = None
    ) -> DBSafetySignalReport:
        sig = DBSafetySignalReport(
            id=uuid.uuid4(),
            corpus_id=corpus_id,
            drug_name=drug_name,
            adverse_reaction_term=adverse_reaction_term,
            system_organ_class=system_organ_class,
            case_count=case_count,
            signal_priority=signal_priority,
            who_umc_causality=who_umc_causality,
            clinical_summary=clinical_summary
        )
        self.session.add(sig)
        await self.session.commit()
        await self.session.refresh(sig)
        return sig

    async def add_metrics(
        self,
        signal_id: uuid.UUID,
        prr: float,
        ror: float,
        ror_lower: float,
        ror_upper: float,
        ic025: float,
        ebgm05: float,
        chi_sq: float
    ) -> DBDisproportionalityMetric:
        metric = DBDisproportionalityMetric(
            id=uuid.uuid4(),
            signal_id=signal_id,
            proportional_reporting_ratio_prr=prr,
            reporting_odds_ratio_ror=ror,
            ror_ci_lower_95=ror_lower,
            ror_ci_upper_95=ror_upper,
            information_component_ic025=ic025,
            ebgm_05=ebgm05,
            chi_square_yates=chi_sq
        )
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric
