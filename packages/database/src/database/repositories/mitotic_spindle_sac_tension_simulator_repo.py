"""Repository for Phase 452: Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.mitotic_spindle_sac_tension_simulator import (
    MitoticSpindleSacTensionStudy,
    MitoticSpindleSacTensionItemProfile,
    MitoticSpindleSacTensionMetricTrace,
)


class MitoticSpindleSacTensionRepository:
    """Database operations for Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Bipolar Mitotic Kinetochore-Microtubule Interface with Mad2/BubR1 Checkpoint Sensor",
        analytical_modality: str = "spindle-assembly-sac-kinetics",
        kinetochore_tension_pico_newtons: float = 38.5,
        mad2_activation_rate_constant_s_inv: float = 0.045,
        anaphase_onset_delay_minutes: float = 18.2,
        spindle_bipolar_alignment_coherence: float = 0.965,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MitoticSpindleSacTensionStudy:
        study = MitoticSpindleSacTensionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            kinetochore_tension_pico_newtons=kinetochore_tension_pico_newtons,
            mad2_activation_rate_constant_s_inv=mad2_activation_rate_constant_s_inv,
            anaphase_onset_delay_minutes=anaphase_onset_delay_minutes,
            spindle_bipolar_alignment_coherence=spindle_bipolar_alignment_coherence,
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
    ) -> MitoticSpindleSacTensionItemProfile:
        item = MitoticSpindleSacTensionItemProfile(
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
    ) -> MitoticSpindleSacTensionMetricTrace:
        trace = MitoticSpindleSacTensionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MitoticSpindleSacTensionStudy]:
        result = await self.session.execute(
            select(MitoticSpindleSacTensionStudy)
            .options(
                selectinload(MitoticSpindleSacTensionStudy.item_profiles),
                selectinload(MitoticSpindleSacTensionStudy.metric_traces),
            )
            .where(MitoticSpindleSacTensionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MitoticSpindleSacTensionStudy]:
        result = await self.session.execute(
            select(MitoticSpindleSacTensionStudy)
            .options(
                selectinload(MitoticSpindleSacTensionStudy.item_profiles),
                selectinload(MitoticSpindleSacTensionStudy.metric_traces),
            )
            .order_by(MitoticSpindleSacTensionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
