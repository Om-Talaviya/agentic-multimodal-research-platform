"""Repository for Phase 528: Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.high_speed_afm_molecular_motor_dynamics import (
    HighSpeedAfmMolecularMotorDynamicsStudy,
    HighSpeedAfmMolecularMotorDynamicsItemProfile,
    HighSpeedAfmMolecularMotorDynamicsMetricTrace,
)


class HighSpeedAfmMolecularMotorDynamicsRepository:
    """Database operations for Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Single Native Myosin V Dimer stepping along Immobilized Actin Filament in Microfluidic HS-AFM Cell",
        analytical_modality: str = "hs-afm-molecular-motor",
        hand_over_hand_step_distance_nm: float = 36.2,
        power_stroke_lever_arm_rotation_deg: float = 72.0,
        afm_cantilever_imaging_rate_fps: float = 12.5,
        atp_limited_dwell_time_ms: float = 42.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> HighSpeedAfmMolecularMotorDynamicsStudy:
        study = HighSpeedAfmMolecularMotorDynamicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            hand_over_hand_step_distance_nm=hand_over_hand_step_distance_nm,
            power_stroke_lever_arm_rotation_deg=power_stroke_lever_arm_rotation_deg,
            afm_cantilever_imaging_rate_fps=afm_cantilever_imaging_rate_fps,
            atp_limited_dwell_time_ms=atp_limited_dwell_time_ms,
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
    ) -> HighSpeedAfmMolecularMotorDynamicsItemProfile:
        item = HighSpeedAfmMolecularMotorDynamicsItemProfile(
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
    ) -> HighSpeedAfmMolecularMotorDynamicsMetricTrace:
        trace = HighSpeedAfmMolecularMotorDynamicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[HighSpeedAfmMolecularMotorDynamicsStudy]:
        stmt = (
            select(HighSpeedAfmMolecularMotorDynamicsStudy)
            .where(HighSpeedAfmMolecularMotorDynamicsStudy.id == study_id)
            .options(
                selectinload(HighSpeedAfmMolecularMotorDynamicsStudy.item_profiles),
                selectinload(HighSpeedAfmMolecularMotorDynamicsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[HighSpeedAfmMolecularMotorDynamicsStudy]:
        stmt = (
            select(HighSpeedAfmMolecularMotorDynamicsStudy)
            .order_by(HighSpeedAfmMolecularMotorDynamicsStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(HighSpeedAfmMolecularMotorDynamicsStudy.item_profiles),
                selectinload(HighSpeedAfmMolecularMotorDynamicsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
