"""Repository for Phase 424: Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.deep_mutational_scanning_epistasis import (
    DeepMutationalScanningEpistasisStudy,
    DeepMutationalScanningEpistasisItemProfile,
    DeepMutationalScanningEpistasisMetricTrace,
)


class DeepMutationalScanningEpistasisRepository:
    """Database operations for Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Beta-Lactamase All-Combinatorial Single/Double Point Mutants",
        analytical_modality: str = "dms-epistasis",
        higher_order_epistasis_coefficient: float = 0.385,
        relative_fitness_enrichment_ratio: float = 2.45,
        delta_delta_g_unfolding_kcal: float = 1.82,
        catalytic_efficiency_retention: float = 0.924,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DeepMutationalScanningEpistasisStudy:
        study = DeepMutationalScanningEpistasisStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            higher_order_epistasis_coefficient=higher_order_epistasis_coefficient,
            relative_fitness_enrichment_ratio=relative_fitness_enrichment_ratio,
            delta_delta_g_unfolding_kcal=delta_delta_g_unfolding_kcal,
            catalytic_efficiency_retention=catalytic_efficiency_retention,
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
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> DeepMutationalScanningEpistasisItemProfile:
        item = DeepMutationalScanningEpistasisItemProfile(
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
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> DeepMutationalScanningEpistasisMetricTrace:
        trace = DeepMutationalScanningEpistasisMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[DeepMutationalScanningEpistasisStudy]:
        result = await self.session.execute(
            select(DeepMutationalScanningEpistasisStudy)
            .options(
                selectinload(DeepMutationalScanningEpistasisStudy.item_profiles),
                selectinload(DeepMutationalScanningEpistasisStudy.metric_traces),
            )
            .where(DeepMutationalScanningEpistasisStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DeepMutationalScanningEpistasisStudy]:
        result = await self.session.execute(
            select(DeepMutationalScanningEpistasisStudy)
            .options(
                selectinload(DeepMutationalScanningEpistasisStudy.item_profiles),
                selectinload(DeepMutationalScanningEpistasisStudy.metric_traces),
            )
            .order_by(DeepMutationalScanningEpistasisStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
