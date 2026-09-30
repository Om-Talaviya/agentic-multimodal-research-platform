"""Repository for Phase 381: Autonomous Single-Cell DNA Methylation and Hydroxymethylation (5mC/5hmC) Bisulfite-Free Caller."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.singlecell_5mc_5hmc_caller import (
    Singlecell5mc5hmcCallerStudy,
    Singlecell5mc5hmcCallerItemProfile,
    Singlecell5mc5hmcCallerMetricTrace,
)


class Singlecell5mc5hmcCallerRepository:
    """Database operations for Autonomous Single-Cell DNA Methylation and Hydroxymethylation (5mC/5hmC) Bisulfite-Free Caller studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "singlecell-5mc-5hmc-caller",
        base_resolution_5hmc_calling_precision_pct: float = 98.4,
        single_cell_cpg_site_coverage_depth_fold: float = 12.5,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> Singlecell5mc5hmcCallerStudy:
        study = Singlecell5mc5hmcCallerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            base_resolution_5hmc_calling_precision_pct=base_resolution_5hmc_calling_precision_pct,
            single_cell_cpg_site_coverage_depth_fold=single_cell_cpg_site_coverage_depth_fold,
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
    ) -> Singlecell5mc5hmcCallerItemProfile:
        item = Singlecell5mc5hmcCallerItemProfile(
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
    ) -> Singlecell5mc5hmcCallerMetricTrace:
        item = Singlecell5mc5hmcCallerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[Singlecell5mc5hmcCallerStudy]:
        stmt = select(Singlecell5mc5hmcCallerStudy).where(Singlecell5mc5hmcCallerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[Singlecell5mc5hmcCallerStudy]:
        stmt = select(Singlecell5mc5hmcCallerStudy).order_by(Singlecell5mc5hmcCallerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
