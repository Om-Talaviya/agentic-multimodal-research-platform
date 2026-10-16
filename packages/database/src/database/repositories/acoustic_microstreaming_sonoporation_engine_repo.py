"""Repository for Phase 564: Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.acoustic_microstreaming_sonoporation_engine import (
    AcousticMicrostreamingSonoporationEngineStudy,
    AcousticMicrostreamingSonoporationEngineItemProfile,
    AcousticMicrostreamingSonoporationEngineMetricTrace,
)


class AcousticMicrostreamingSonoporationEngineRepository:
    """Database operations for Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Suspended Human CD34+ Hematopoietic Stem Cells and Phospholipid Microbubbles subjected to 1-MHz Focused Acoustic Waves",
        analytical_modality: str = "acoustic-microstreaming-sonoporation",
        intracellular_delivery_efficiency_pct: float = 92.4,
        cell_membrane_resealing_time_seconds: float = 38.0,
        acoustic_cavitation_shear_stress_kpa: float = 18.5,
        post_sonoporation_cell_viability_pct: float = 94.8,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> AcousticMicrostreamingSonoporationEngineStudy:
        study = AcousticMicrostreamingSonoporationEngineStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            intracellular_delivery_efficiency_pct=intracellular_delivery_efficiency_pct,
            cell_membrane_resealing_time_seconds=cell_membrane_resealing_time_seconds,
            acoustic_cavitation_shear_stress_kpa=acoustic_cavitation_shear_stress_kpa,
            post_sonoporation_cell_viability_pct=post_sonoporation_cell_viability_pct,
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
    ) -> AcousticMicrostreamingSonoporationEngineItemProfile:
        item = AcousticMicrostreamingSonoporationEngineItemProfile(
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
    ) -> AcousticMicrostreamingSonoporationEngineMetricTrace:
        trace = AcousticMicrostreamingSonoporationEngineMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[AcousticMicrostreamingSonoporationEngineStudy]:
        stmt = (
            select(AcousticMicrostreamingSonoporationEngineStudy)
            .where(AcousticMicrostreamingSonoporationEngineStudy.id == study_id)
            .options(
                selectinload(AcousticMicrostreamingSonoporationEngineStudy.item_profiles),
                selectinload(AcousticMicrostreamingSonoporationEngineStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[AcousticMicrostreamingSonoporationEngineStudy]:
        stmt = (
            select(AcousticMicrostreamingSonoporationEngineStudy)
            .order_by(AcousticMicrostreamingSonoporationEngineStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(AcousticMicrostreamingSonoporationEngineStudy.item_profiles),
                selectinload(AcousticMicrostreamingSonoporationEngineStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
