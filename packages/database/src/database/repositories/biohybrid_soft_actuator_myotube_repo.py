"""Repository for Phase 457: Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.biohybrid_soft_actuator_myotube import (
    BiohybridSoftActuatorMyotubeStudy,
    BiohybridSoftActuatorMyotubeItemProfile,
    BiohybridSoftActuatorMyotubeMetricTrace,
)


class BiohybridSoftActuatorMyotubeRepository:
    """Database operations for Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "3D Bioprinted Optogenetic C2C12 Skeletal Myotube Cantilever on Flexible Hydrogel Skeleton",
        analytical_modality: str = "biohybrid-actuator-mechanics",
        active_contractile_force_micro_newtons: float = 285.0,
        twitch_to_tetanus_force_ratio: float = 0.34,
        cyclic_fatigue_endurance_cycles: float = 12500.0,
        electromechanical_coupling_efficiency: float = 0.912,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BiohybridSoftActuatorMyotubeStudy:
        study = BiohybridSoftActuatorMyotubeStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            active_contractile_force_micro_newtons=active_contractile_force_micro_newtons,
            twitch_to_tetanus_force_ratio=twitch_to_tetanus_force_ratio,
            cyclic_fatigue_endurance_cycles=cyclic_fatigue_endurance_cycles,
            electromechanical_coupling_efficiency=electromechanical_coupling_efficiency,
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
    ) -> BiohybridSoftActuatorMyotubeItemProfile:
        item = BiohybridSoftActuatorMyotubeItemProfile(
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
    ) -> BiohybridSoftActuatorMyotubeMetricTrace:
        trace = BiohybridSoftActuatorMyotubeMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BiohybridSoftActuatorMyotubeStudy]:
        result = await self.session.execute(
            select(BiohybridSoftActuatorMyotubeStudy)
            .options(
                selectinload(BiohybridSoftActuatorMyotubeStudy.item_profiles),
                selectinload(BiohybridSoftActuatorMyotubeStudy.metric_traces),
            )
            .where(BiohybridSoftActuatorMyotubeStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[BiohybridSoftActuatorMyotubeStudy]:
        result = await self.session.execute(
            select(BiohybridSoftActuatorMyotubeStudy)
            .options(
                selectinload(BiohybridSoftActuatorMyotubeStudy.item_profiles),
                selectinload(BiohybridSoftActuatorMyotubeStudy.metric_traces),
            )
            .order_by(BiohybridSoftActuatorMyotubeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
