"""Repository for Phase 546: Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.epigenetic_reprogramming_yamanaka_factor_kinetics import (
    EpigeneticReprogrammingYamanakaFactorKineticsStudy,
    EpigeneticReprogrammingYamanakaFactorKineticsItemProfile,
    EpigeneticReprogrammingYamanakaFactorKineticsMetricTrace,
)


class EpigeneticReprogrammingYamanakaFactorKineticsRepository:
    """Database operations for Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Single-Cell Doxycycline-Inducible OSKM Human Dermal Fibroblasts tracked across 21 Days",
        analytical_modality: str = "yamanaka-reprogramming-kinetics",
        fully_reprogrammed_naive_pluripotency_rate_pct: float = 8.5,
        oct4_sox2_pioneer_chromatin_dwell_time_s: float = 32.0,
        dna_methylation_clock_reversal_years: float = 45.0,
        trajectory_waddington_barrier_crossing_prob: float = 0.14,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> EpigeneticReprogrammingYamanakaFactorKineticsStudy:
        study = EpigeneticReprogrammingYamanakaFactorKineticsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            fully_reprogrammed_naive_pluripotency_rate_pct=fully_reprogrammed_naive_pluripotency_rate_pct,
            oct4_sox2_pioneer_chromatin_dwell_time_s=oct4_sox2_pioneer_chromatin_dwell_time_s,
            dna_methylation_clock_reversal_years=dna_methylation_clock_reversal_years,
            trajectory_waddington_barrier_crossing_prob=trajectory_waddington_barrier_crossing_prob,
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
    ) -> EpigeneticReprogrammingYamanakaFactorKineticsItemProfile:
        item = EpigeneticReprogrammingYamanakaFactorKineticsItemProfile(
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
    ) -> EpigeneticReprogrammingYamanakaFactorKineticsMetricTrace:
        trace = EpigeneticReprogrammingYamanakaFactorKineticsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[EpigeneticReprogrammingYamanakaFactorKineticsStudy]:
        stmt = (
            select(EpigeneticReprogrammingYamanakaFactorKineticsStudy)
            .where(EpigeneticReprogrammingYamanakaFactorKineticsStudy.id == study_id)
            .options(
                selectinload(EpigeneticReprogrammingYamanakaFactorKineticsStudy.item_profiles),
                selectinload(EpigeneticReprogrammingYamanakaFactorKineticsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[EpigeneticReprogrammingYamanakaFactorKineticsStudy]:
        stmt = (
            select(EpigeneticReprogrammingYamanakaFactorKineticsStudy)
            .order_by(EpigeneticReprogrammingYamanakaFactorKineticsStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(EpigeneticReprogrammingYamanakaFactorKineticsStudy.item_profiles),
                selectinload(EpigeneticReprogrammingYamanakaFactorKineticsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
