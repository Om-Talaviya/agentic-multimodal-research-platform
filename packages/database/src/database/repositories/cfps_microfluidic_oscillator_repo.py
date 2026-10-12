"""Repository for Phase 425: Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cfps_microfluidic_oscillator import (
    CfpsMicrofluidicOscillatorStudy,
    CfpsMicrofluidicOscillatorItemProfile,
    CfpsMicrofluidicOscillatorMetricTrace,
)


class CfpsMicrofluidicOscillatorRepository:
    """Database operations for Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Microfluidic Droplet Array with Repressilator TX-TL Reaction",
        analytical_modality: str = "cfps-microfluidic-oscillator",
        oscillation_period_minutes: float = 124.0,
        fluorescent_reporter_amplitude_rfu: float = 4850.0,
        reaction_dwell_stability_score: float = 0.965,
        damping_decay_coefficient: float = 0.042,
        confidence_score: float = 0.983,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CfpsMicrofluidicOscillatorStudy:
        study = CfpsMicrofluidicOscillatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            oscillation_period_minutes=oscillation_period_minutes,
            fluorescent_reporter_amplitude_rfu=fluorescent_reporter_amplitude_rfu,
            reaction_dwell_stability_score=reaction_dwell_stability_score,
            damping_decay_coefficient=damping_decay_coefficient,
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
    ) -> CfpsMicrofluidicOscillatorItemProfile:
        item = CfpsMicrofluidicOscillatorItemProfile(
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
    ) -> CfpsMicrofluidicOscillatorMetricTrace:
        trace = CfpsMicrofluidicOscillatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CfpsMicrofluidicOscillatorStudy]:
        result = await self.session.execute(
            select(CfpsMicrofluidicOscillatorStudy)
            .options(
                selectinload(CfpsMicrofluidicOscillatorStudy.item_profiles),
                selectinload(CfpsMicrofluidicOscillatorStudy.metric_traces),
            )
            .where(CfpsMicrofluidicOscillatorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CfpsMicrofluidicOscillatorStudy]:
        result = await self.session.execute(
            select(CfpsMicrofluidicOscillatorStudy)
            .options(
                selectinload(CfpsMicrofluidicOscillatorStudy.item_profiles),
                selectinload(CfpsMicrofluidicOscillatorStudy.metric_traces),
            )
            .order_by(CfpsMicrofluidicOscillatorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
