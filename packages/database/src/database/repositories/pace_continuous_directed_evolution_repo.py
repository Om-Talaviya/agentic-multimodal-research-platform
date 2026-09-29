"""Repository for Phase 288: Autonomous Continuous Directed Protein Evolution (PACE) Phage Mutagenesis & Selection Velocity Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pace_continuous_directed_evolution import (
    PaceContinuousDirectedEvolutionStudy,
    PaceContinuousDirectedEvolutionItemProfile,
    PaceContinuousDirectedEvolutionMetricTrace,
)


class PaceContinuousDirectedEvolutionRepository:
    """Database operations for Autonomous Continuous Directed Protein Evolution (PACE) Phage Mutagenesis & Selection Velocity Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "pace-continuous-directed-evolution",
        selection_velocity_generations_per_hour: float = 4.8,
        evolved_variant_fitness_gain_fold: float = 32.5,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PaceContinuousDirectedEvolutionStudy:
        study = PaceContinuousDirectedEvolutionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            selection_velocity_generations_per_hour=selection_velocity_generations_per_hour,
            evolved_variant_fitness_gain_fold=evolved_variant_fitness_gain_fold,
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
    ) -> PaceContinuousDirectedEvolutionItemProfile:
        item = PaceContinuousDirectedEvolutionItemProfile(
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
    ) -> PaceContinuousDirectedEvolutionMetricTrace:
        item = PaceContinuousDirectedEvolutionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PaceContinuousDirectedEvolutionStudy]:
        stmt = select(PaceContinuousDirectedEvolutionStudy).where(PaceContinuousDirectedEvolutionStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[PaceContinuousDirectedEvolutionStudy]:
        stmt = select(PaceContinuousDirectedEvolutionStudy).order_by(PaceContinuousDirectedEvolutionStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
