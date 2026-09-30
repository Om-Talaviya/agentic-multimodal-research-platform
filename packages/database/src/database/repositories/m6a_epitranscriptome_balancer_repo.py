"""Repository for Phase 389: Autonomous Whole-Transcriptome m6A Methyltransferase & Demethylase Dynamic Balance Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.m6a_epitranscriptome_balancer import (
    M6aEpitranscriptomeBalancerStudy,
    M6aEpitranscriptomeBalancerItemProfile,
    M6aEpitranscriptomeBalancerMetricTrace,
)


class M6aEpitranscriptomeBalancerRepository:
    """Database operations for Autonomous Whole-Transcriptome m6A Methyltransferase & Demethylase Dynamic Balance Simulator studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "m6a-epitranscriptome-balancer",
        transcriptome_wide_m6a_stoichiometric_fidelity_pct: float = 97.8,
        target_mrna_decay_half_life_modulation_fold: float = 3.4,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> M6aEpitranscriptomeBalancerStudy:
        study = M6aEpitranscriptomeBalancerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            transcriptome_wide_m6a_stoichiometric_fidelity_pct=transcriptome_wide_m6a_stoichiometric_fidelity_pct,
            target_mrna_decay_half_life_modulation_fold=target_mrna_decay_half_life_modulation_fold,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> M6aEpitranscriptomeBalancerItemProfile:
        item = M6aEpitranscriptomeBalancerItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> M6aEpitranscriptomeBalancerMetricTrace:
        item = M6aEpitranscriptomeBalancerMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[M6aEpitranscriptomeBalancerStudy]:
        stmt = select(M6aEpitranscriptomeBalancerStudy).where(M6aEpitranscriptomeBalancerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[M6aEpitranscriptomeBalancerStudy]:
        stmt = select(M6aEpitranscriptomeBalancerStudy).order_by(M6aEpitranscriptomeBalancerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
