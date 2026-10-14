"""Repository for Phase 472: Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.gene_circuit_bistable_switch import (
    GeneCircuitBistableSwitchStudy,
    GeneCircuitBistableSwitchItemProfile,
    GeneCircuitBistableSwitchMetricTrace,
)


class GeneCircuitBistableSwitchRepository:
    """Database operations for Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Synthetic LacI-TetR Mutual Inactivation Toggle Switch with Epigenetic DNA Methylation Memory",
        analytical_modality: str = "gene-circuit-bistable-switch",
        bistable_hysteresis_basin_depth_au: float = 4.85,
        stochastic_switching_barrier_height_kbT: float = 18.2,
        state_transition_retention_half_life_hours: float = 144.0,
        cooperative_hill_coefficient: float = 2.85,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> GeneCircuitBistableSwitchStudy:
        study = GeneCircuitBistableSwitchStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            bistable_hysteresis_basin_depth_au=bistable_hysteresis_basin_depth_au,
            stochastic_switching_barrier_height_kbT=stochastic_switching_barrier_height_kbT,
            state_transition_retention_half_life_hours=state_transition_retention_half_life_hours,
            cooperative_hill_coefficient=cooperative_hill_coefficient,
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
    ) -> GeneCircuitBistableSwitchItemProfile:
        item = GeneCircuitBistableSwitchItemProfile(
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
    ) -> GeneCircuitBistableSwitchMetricTrace:
        trace = GeneCircuitBistableSwitchMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[GeneCircuitBistableSwitchStudy]:
        result = await self.session.execute(
            select(GeneCircuitBistableSwitchStudy)
            .options(
                selectinload(GeneCircuitBistableSwitchStudy.item_profiles),
                selectinload(GeneCircuitBistableSwitchStudy.metric_traces),
            )
            .where(GeneCircuitBistableSwitchStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[GeneCircuitBistableSwitchStudy]:
        result = await self.session.execute(
            select(GeneCircuitBistableSwitchStudy)
            .options(
                selectinload(GeneCircuitBistableSwitchStudy.item_profiles),
                selectinload(GeneCircuitBistableSwitchStudy.metric_traces),
            )
            .order_by(GeneCircuitBistableSwitchStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
