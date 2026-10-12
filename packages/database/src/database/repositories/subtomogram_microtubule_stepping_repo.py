"""Repository for Phase 418: Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.subtomogram_microtubule_stepping import (
    SubtomogramMicrotubuleSteppingStudy,
    SubtomogramMicrotubuleSteppingItemProfile,
    SubtomogramMicrotubuleSteppingMetricTrace,
)


class SubtomogramMicrotubuleSteppingRepository:
    """Database operations for Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Axonemal 13-Protofilament Microtubule with Kinesin-1 Dimers",
        analytical_modality: str = "subtomogram-microtubule",
        subtomogram_resolution_angstrom: float = 3.85,
        motor_step_size_nm: float = 8.12,
        protofilament_twist_angle_deg: float = 0.28,
        stepping_dwell_time_ms: float = 18.5,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SubtomogramMicrotubuleSteppingStudy:
        study = SubtomogramMicrotubuleSteppingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            subtomogram_resolution_angstrom=subtomogram_resolution_angstrom,
            motor_step_size_nm=motor_step_size_nm,
            protofilament_twist_angle_deg=protofilament_twist_angle_deg,
            stepping_dwell_time_ms=stepping_dwell_time_ms,
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
    ) -> SubtomogramMicrotubuleSteppingItemProfile:
        item = SubtomogramMicrotubuleSteppingItemProfile(
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
    ) -> SubtomogramMicrotubuleSteppingMetricTrace:
        trace = SubtomogramMicrotubuleSteppingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SubtomogramMicrotubuleSteppingStudy]:
        result = await self.session.execute(
            select(SubtomogramMicrotubuleSteppingStudy)
            .options(
                selectinload(SubtomogramMicrotubuleSteppingStudy.item_profiles),
                selectinload(SubtomogramMicrotubuleSteppingStudy.metric_traces),
            )
            .where(SubtomogramMicrotubuleSteppingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SubtomogramMicrotubuleSteppingStudy]:
        result = await self.session.execute(
            select(SubtomogramMicrotubuleSteppingStudy)
            .options(
                selectinload(SubtomogramMicrotubuleSteppingStudy.item_profiles),
                selectinload(SubtomogramMicrotubuleSteppingStudy.metric_traces),
            )
            .order_by(SubtomogramMicrotubuleSteppingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
