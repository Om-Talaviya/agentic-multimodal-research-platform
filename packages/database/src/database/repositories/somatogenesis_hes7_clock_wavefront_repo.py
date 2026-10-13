"""Repository for Phase 471: Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.somatogenesis_hes7_clock_wavefront import (
    SomatogenesisHes7ClockWavefrontStudy,
    SomatogenesisHes7ClockWavefrontItemProfile,
    SomatogenesisHes7ClockWavefrontMetricTrace,
)


class SomatogenesisHes7ClockWavefrontRepository:
    """Database operations for Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Synthetic Presomitic Mesoderm (PSM) Microtissue Organoid with Oscillatory Hes7-Venus Reporter",
        analytical_modality: str = "somatogenesis-clock-wavefront",
        clock_oscillation_periodicity_minutes: float = 124.0,
        wavefront_propagation_velocity_um_per_hr: float = 48.5,
        somite_boundary_sharpness_contrast_ratio: float = 4.15,
        synchronization_kuramoto_order_parameter: float = 0.942,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SomatogenesisHes7ClockWavefrontStudy:
        study = SomatogenesisHes7ClockWavefrontStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            clock_oscillation_periodicity_minutes=clock_oscillation_periodicity_minutes,
            wavefront_propagation_velocity_um_per_hr=wavefront_propagation_velocity_um_per_hr,
            somite_boundary_sharpness_contrast_ratio=somite_boundary_sharpness_contrast_ratio,
            synchronization_kuramoto_order_parameter=synchronization_kuramoto_order_parameter,
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
    ) -> SomatogenesisHes7ClockWavefrontItemProfile:
        item = SomatogenesisHes7ClockWavefrontItemProfile(
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
    ) -> SomatogenesisHes7ClockWavefrontMetricTrace:
        trace = SomatogenesisHes7ClockWavefrontMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SomatogenesisHes7ClockWavefrontStudy]:
        result = await self.session.execute(
            select(SomatogenesisHes7ClockWavefrontStudy)
            .options(
                selectinload(SomatogenesisHes7ClockWavefrontStudy.item_profiles),
                selectinload(SomatogenesisHes7ClockWavefrontStudy.metric_traces),
            )
            .where(SomatogenesisHes7ClockWavefrontStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SomatogenesisHes7ClockWavefrontStudy]:
        result = await self.session.execute(
            select(SomatogenesisHes7ClockWavefrontStudy)
            .options(
                selectinload(SomatogenesisHes7ClockWavefrontStudy.item_profiles),
                selectinload(SomatogenesisHes7ClockWavefrontStudy.metric_traces),
            )
            .order_by(SomatogenesisHes7ClockWavefrontStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
