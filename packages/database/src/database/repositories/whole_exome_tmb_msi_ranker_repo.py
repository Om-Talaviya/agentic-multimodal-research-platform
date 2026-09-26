"""Repository for Phase 218: Autonomous Whole-Exome Sequencing (WES) Tumor Mutation Burden (TMB) & Microsatellite Instability (MSI) Ranker Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.whole_exome_tmb_msi_ranker import (
    WholeExomeTmbMsiRankerStudy,
    WholeExomeTmbMsiRankerItemProfile,
    WholeExomeTmbMsiRankerMetricTrace,
)


class WholeExomeTmbMsiRankerRepository:
    """Database operations for Autonomous Whole-Exome Sequencing (WES) Tumor Mutation Burden (TMB) & Microsatellite Instability (MSI) Ranker Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "whole-exome-tmb-msi-ranker",
        tmb_mutations_per_mb: float = 28.4,
        msi_instability_score_pct: float = 94.2,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> WholeExomeTmbMsiRankerStudy:
        study = WholeExomeTmbMsiRankerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            tmb_mutations_per_mb=tmb_mutations_per_mb,
            msi_instability_score_pct=msi_instability_score_pct,
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
    ) -> WholeExomeTmbMsiRankerItemProfile:
        item = WholeExomeTmbMsiRankerItemProfile(
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
    ) -> WholeExomeTmbMsiRankerMetricTrace:
        item = WholeExomeTmbMsiRankerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[WholeExomeTmbMsiRankerStudy]:
        stmt = select(WholeExomeTmbMsiRankerStudy).where(WholeExomeTmbMsiRankerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[WholeExomeTmbMsiRankerStudy]:
        stmt = select(WholeExomeTmbMsiRankerStudy).order_by(WholeExomeTmbMsiRankerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
