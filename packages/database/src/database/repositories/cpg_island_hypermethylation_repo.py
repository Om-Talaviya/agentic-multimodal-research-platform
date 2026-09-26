"""Repository for Phase 212: Autonomous Epigenomic Promoter CpG Island Hypermethylation & Tumor Suppressor Gene Silencing Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cpg_island_hypermethylation import (
    CpGIslandHypermethylationStudy,
    CpGIslandHypermethylationItemProfile,
    CpGIslandHypermethylationMetricTrace,
)


class CpGIslandHypermethylationRepository:
    """Database operations for Autonomous Epigenomic Promoter CpG Island Hypermethylation & Tumor Suppressor Gene Silencing Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "cpg-island-hypermethylation",
        silencing_repression_pct: float = 96.7,
        methylation_density_beta: float = 0.89,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CpGIslandHypermethylationStudy:
        study = CpGIslandHypermethylationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            silencing_repression_pct=silencing_repression_pct,
            methylation_density_beta=methylation_density_beta,
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
    ) -> CpGIslandHypermethylationItemProfile:
        item = CpGIslandHypermethylationItemProfile(
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
    ) -> CpGIslandHypermethylationMetricTrace:
        item = CpGIslandHypermethylationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CpGIslandHypermethylationStudy]:
        stmt = select(CpGIslandHypermethylationStudy).where(CpGIslandHypermethylationStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CpGIslandHypermethylationStudy]:
        stmt = select(CpGIslandHypermethylationStudy).order_by(CpGIslandHypermethylationStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
