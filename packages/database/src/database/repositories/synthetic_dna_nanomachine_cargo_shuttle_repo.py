"""Repository for Phase 523: Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_dna_nanomachine_cargo_shuttle import (
    SyntheticDnaNanomachineCargoShuttleStudy,
    SyntheticDnaNanomachineCargoShuttleItemProfile,
    SyntheticDnaNanomachineCargoShuttleMetricTrace,
)


class SyntheticDnaNanomachineCargoShuttleRepository:
    """Database operations for Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Scaffolded DNA Origami 2D Origami Track with Autonomous Kinesin-Mimic Fuel-Fueled DNA Bipedal Walker",
        analytical_modality: str = "dna-nanomachine-shuttle",
        walker_directional_velocity_nm_per_min: float = 18.0,
        fuel_strand_consumption_efficiency: float = 0.965,
        molecular_cargo_handover_fidelity_pct: float = 98.4,
        continuous_processive_stepping_distance_nm: float = 320.0,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticDnaNanomachineCargoShuttleStudy:
        study = SyntheticDnaNanomachineCargoShuttleStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            walker_directional_velocity_nm_per_min=walker_directional_velocity_nm_per_min,
            fuel_strand_consumption_efficiency=fuel_strand_consumption_efficiency,
            molecular_cargo_handover_fidelity_pct=molecular_cargo_handover_fidelity_pct,
            continuous_processive_stepping_distance_nm=continuous_processive_stepping_distance_nm,
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
    ) -> SyntheticDnaNanomachineCargoShuttleItemProfile:
        item = SyntheticDnaNanomachineCargoShuttleItemProfile(
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
    ) -> SyntheticDnaNanomachineCargoShuttleMetricTrace:
        trace = SyntheticDnaNanomachineCargoShuttleMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticDnaNanomachineCargoShuttleStudy]:
        result = await self.session.execute(
            select(SyntheticDnaNanomachineCargoShuttleStudy)
            .options(
                selectinload(SyntheticDnaNanomachineCargoShuttleStudy.item_profiles),
                selectinload(SyntheticDnaNanomachineCargoShuttleStudy.metric_traces),
            )
            .where(SyntheticDnaNanomachineCargoShuttleStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SyntheticDnaNanomachineCargoShuttleStudy]:
        result = await self.session.execute(
            select(SyntheticDnaNanomachineCargoShuttleStudy)
            .options(
                selectinload(SyntheticDnaNanomachineCargoShuttleStudy.item_profiles),
                selectinload(SyntheticDnaNanomachineCargoShuttleStudy.metric_traces),
            )
            .order_by(SyntheticDnaNanomachineCargoShuttleStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
