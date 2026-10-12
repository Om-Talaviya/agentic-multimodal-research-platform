"""Repository for Phase 439: Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bacterial_chemotaxis_run_tumble_simulator import (
    BacterialChemotaxisSimulatorStudy,
    BacterialChemotaxisSimulatorItemProfile,
    BacterialChemotaxisSimulatorMetricTrace,
)


class BacterialChemotaxisSimulatorRepository:
    """Database operations for Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "E. coli K-12 Motile Swarm in Microfluidic Attractant/Repellent Gradient",
        analytical_modality: str = "chemotaxis-run-tumble",
        run_duration_mean_seconds: float = 1.25,
        tumble_frequency_hz: float = 0.45,
        chemotactic_drift_velocity_um_per_s: float = 8.42,
        chey_p_phosphorylation_equilibrium: float = 0.32,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BacterialChemotaxisSimulatorStudy:
        study = BacterialChemotaxisSimulatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            run_duration_mean_seconds=run_duration_mean_seconds,
            tumble_frequency_hz=tumble_frequency_hz,
            chemotactic_drift_velocity_um_per_s=chemotactic_drift_velocity_um_per_s,
            chey_p_phosphorylation_equilibrium=chey_p_phosphorylation_equilibrium,
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
    ) -> BacterialChemotaxisSimulatorItemProfile:
        item = BacterialChemotaxisSimulatorItemProfile(
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
    ) -> BacterialChemotaxisSimulatorMetricTrace:
        trace = BacterialChemotaxisSimulatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BacterialChemotaxisSimulatorStudy]:
        result = await self.session.execute(
            select(BacterialChemotaxisSimulatorStudy)
            .options(
                selectinload(BacterialChemotaxisSimulatorStudy.item_profiles),
                selectinload(BacterialChemotaxisSimulatorStudy.metric_traces),
            )
            .where(BacterialChemotaxisSimulatorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[BacterialChemotaxisSimulatorStudy]:
        result = await self.session.execute(
            select(BacterialChemotaxisSimulatorStudy)
            .options(
                selectinload(BacterialChemotaxisSimulatorStudy.item_profiles),
                selectinload(BacterialChemotaxisSimulatorStudy.metric_traces),
            )
            .order_by(BacterialChemotaxisSimulatorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
