"""Repository for Phase 432: Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pace_directed_evolution_trajectory import (
    PaceDirectedEvolutionTrajectoryStudy,
    PaceDirectedEvolutionTrajectoryItemProfile,
    PaceDirectedEvolutionTrajectoryMetricTrace,
)


class PaceDirectedEvolutionTrajectoryRepository:
    """Database operations for Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Continuous Chemostat Lago Lagoon Phage Population",
        analytical_modality: str = "pace-directed-evolution",
        selection_stringency_factor: float = 4.85,
        mutational_drift_velocity_subs_per_hr: float = 0.32,
        fitness_enrichment_trajectory_fold: float = 84.0,
        lagoon_dilution_rate_vol_per_hr: float = 2.1,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PaceDirectedEvolutionTrajectoryStudy:
        study = PaceDirectedEvolutionTrajectoryStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            selection_stringency_factor=selection_stringency_factor,
            mutational_drift_velocity_subs_per_hr=mutational_drift_velocity_subs_per_hr,
            fitness_enrichment_trajectory_fold=fitness_enrichment_trajectory_fold,
            lagoon_dilution_rate_vol_per_hr=lagoon_dilution_rate_vol_per_hr,
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
    ) -> PaceDirectedEvolutionTrajectoryItemProfile:
        item = PaceDirectedEvolutionTrajectoryItemProfile(
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
    ) -> PaceDirectedEvolutionTrajectoryMetricTrace:
        trace = PaceDirectedEvolutionTrajectoryMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PaceDirectedEvolutionTrajectoryStudy]:
        result = await self.session.execute(
            select(PaceDirectedEvolutionTrajectoryStudy)
            .options(
                selectinload(PaceDirectedEvolutionTrajectoryStudy.item_profiles),
                selectinload(PaceDirectedEvolutionTrajectoryStudy.metric_traces),
            )
            .where(PaceDirectedEvolutionTrajectoryStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[PaceDirectedEvolutionTrajectoryStudy]:
        result = await self.session.execute(
            select(PaceDirectedEvolutionTrajectoryStudy)
            .options(
                selectinload(PaceDirectedEvolutionTrajectoryStudy.item_profiles),
                selectinload(PaceDirectedEvolutionTrajectoryStudy.metric_traces),
            )
            .order_by(PaceDirectedEvolutionTrajectoryStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
