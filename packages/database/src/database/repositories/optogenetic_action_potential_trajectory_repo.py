"""Repository for Phase 444: Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.optogenetic_action_potential_trajectory import (
    OptogeneticActionPotentialStudy,
    OptogeneticActionPotentialItemProfile,
    OptogeneticActionPotentialMetricTrace,
)


class OptogeneticActionPotentialRepository:
    """Database operations for Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Channelrhodopsin-2 (ChR2) Expressing Cortical Pyramidal Neurons under 470nm Pulsed Blue Light",
        analytical_modality: str = "optogenetic-membrane-depolarization",
        membrane_depolarization_rate_mv_per_ms: float = 18.4,
        action_potential_firing_fidelity: float = 0.982,
        photocurrent_amplitude_pA: float = 840.0,
        channel_closing_decay_tau_off_ms: float = 11.2,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OptogeneticActionPotentialStudy:
        study = OptogeneticActionPotentialStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            membrane_depolarization_rate_mv_per_ms=membrane_depolarization_rate_mv_per_ms,
            action_potential_firing_fidelity=action_potential_firing_fidelity,
            photocurrent_amplitude_pA=photocurrent_amplitude_pA,
            channel_closing_decay_tau_off_ms=channel_closing_decay_tau_off_ms,
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
    ) -> OptogeneticActionPotentialItemProfile:
        item = OptogeneticActionPotentialItemProfile(
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
    ) -> OptogeneticActionPotentialMetricTrace:
        trace = OptogeneticActionPotentialMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OptogeneticActionPotentialStudy]:
        result = await self.session.execute(
            select(OptogeneticActionPotentialStudy)
            .options(
                selectinload(OptogeneticActionPotentialStudy.item_profiles),
                selectinload(OptogeneticActionPotentialStudy.metric_traces),
            )
            .where(OptogeneticActionPotentialStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[OptogeneticActionPotentialStudy]:
        result = await self.session.execute(
            select(OptogeneticActionPotentialStudy)
            .options(
                selectinload(OptogeneticActionPotentialStudy.item_profiles),
                selectinload(OptogeneticActionPotentialStudy.metric_traces),
            )
            .order_by(OptogeneticActionPotentialStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
