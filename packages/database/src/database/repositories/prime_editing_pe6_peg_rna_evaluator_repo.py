"""Repository for Phase 310: Autonomous Next-Gen Prime Editing (PE6/PE7) Dual-Engineered pegRNA Design & Transversion Optimization Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.prime_editing_pe6_peg_rna_evaluator import (
    PrimeEditingPe6PegRnaEvaluatorStudy,
    PrimeEditingPe6PegRnaEvaluatorItemProfile,
    PrimeEditingPe6PegRnaEvaluatorMetricTrace,
)


class PrimeEditingPe6PegRnaEvaluatorRepository:
    """Database operations for Autonomous Next-Gen Prime Editing (PE6/PE7) Dual-Engineered pegRNA Design & Transversion Optimization Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "prime-editing-pe6-peg-rna",
        prime_editing_efficiency_pct: float = 89.6,
        bystander_indel_frequency_pct: float = 0.12,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PrimeEditingPe6PegRnaEvaluatorStudy:
        study = PrimeEditingPe6PegRnaEvaluatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            prime_editing_efficiency_pct=prime_editing_efficiency_pct,
            bystander_indel_frequency_pct=bystander_indel_frequency_pct,
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
    ) -> PrimeEditingPe6PegRnaEvaluatorItemProfile:
        item = PrimeEditingPe6PegRnaEvaluatorItemProfile(
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
    ) -> PrimeEditingPe6PegRnaEvaluatorMetricTrace:
        item = PrimeEditingPe6PegRnaEvaluatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PrimeEditingPe6PegRnaEvaluatorStudy]:
        stmt = select(PrimeEditingPe6PegRnaEvaluatorStudy).where(PrimeEditingPe6PegRnaEvaluatorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[PrimeEditingPe6PegRnaEvaluatorStudy]:
        stmt = select(PrimeEditingPe6PegRnaEvaluatorStudy).order_by(PrimeEditingPe6PegRnaEvaluatorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
