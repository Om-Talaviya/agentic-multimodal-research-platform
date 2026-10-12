"""Repository for Phase 440: Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.super_resolution_minflux_nanometer_tracking import (
    MinfluxNanometerTrackingStudy,
    MinfluxNanometerTrackingItemProfile,
    MinfluxNanometerTrackingMetricTrace,
)


class MinfluxNanometerTrackingRepository:
    """Database operations for Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Living Motor Protein Myosin V Moving Along Actin Filament with Cy5 Label",
        analytical_modality: str = "minflux-tracking",
        spatial_localization_precision_angstrom: float = 8.5,
        temporal_resolution_us: float = 120.0,
        photon_budget_efficiency_ratio: float = 0.942,
        step_size_hand_over_hand_nm: float = 36.2,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MinfluxNanometerTrackingStudy:
        study = MinfluxNanometerTrackingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            spatial_localization_precision_angstrom=spatial_localization_precision_angstrom,
            temporal_resolution_us=temporal_resolution_us,
            photon_budget_efficiency_ratio=photon_budget_efficiency_ratio,
            step_size_hand_over_hand_nm=step_size_hand_over_hand_nm,
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
    ) -> MinfluxNanometerTrackingItemProfile:
        item = MinfluxNanometerTrackingItemProfile(
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
    ) -> MinfluxNanometerTrackingMetricTrace:
        trace = MinfluxNanometerTrackingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MinfluxNanometerTrackingStudy]:
        result = await self.session.execute(
            select(MinfluxNanometerTrackingStudy)
            .options(
                selectinload(MinfluxNanometerTrackingStudy.item_profiles),
                selectinload(MinfluxNanometerTrackingStudy.metric_traces),
            )
            .where(MinfluxNanometerTrackingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MinfluxNanometerTrackingStudy]:
        result = await self.session.execute(
            select(MinfluxNanometerTrackingStudy)
            .options(
                selectinload(MinfluxNanometerTrackingStudy.item_profiles),
                selectinload(MinfluxNanometerTrackingStudy.metric_traces),
            )
            .order_by(MinfluxNanometerTrackingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
