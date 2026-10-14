"""Repository for Phase 474: Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.kinesin_dynein_vesicle_transport import (
    KinesinDyneinVesicleTransportStudy,
    KinesinDyneinVesicleTransportItemProfile,
    KinesinDyneinVesicleTransportMetricTrace,
)


class KinesinDyneinVesicleTransportRepository:
    """Database operations for Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Axonal Microtubule Filament with Dual Kinesin-1 and Cytoplasmic Dynein Vesicle Cargo",
        analytical_modality: str = "kinesin-dynein-tug-of-war",
        anterograde_retrograde_velocity_ratio: float = 1.42,
        motor_detachment_stall_force_pN: float = 7.2,
        mean_run_length_processivity_um: float = 3.85,
        tug_of_war_cooperative_coordination_index: float = 0.915,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> KinesinDyneinVesicleTransportStudy:
        study = KinesinDyneinVesicleTransportStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            anterograde_retrograde_velocity_ratio=anterograde_retrograde_velocity_ratio,
            motor_detachment_stall_force_pN=motor_detachment_stall_force_pN,
            mean_run_length_processivity_um=mean_run_length_processivity_um,
            tug_of_war_cooperative_coordination_index=tug_of_war_cooperative_coordination_index,
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
    ) -> KinesinDyneinVesicleTransportItemProfile:
        item = KinesinDyneinVesicleTransportItemProfile(
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
    ) -> KinesinDyneinVesicleTransportMetricTrace:
        trace = KinesinDyneinVesicleTransportMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[KinesinDyneinVesicleTransportStudy]:
        result = await self.session.execute(
            select(KinesinDyneinVesicleTransportStudy)
            .options(
                selectinload(KinesinDyneinVesicleTransportStudy.item_profiles),
                selectinload(KinesinDyneinVesicleTransportStudy.metric_traces),
            )
            .where(KinesinDyneinVesicleTransportStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[KinesinDyneinVesicleTransportStudy]:
        result = await self.session.execute(
            select(KinesinDyneinVesicleTransportStudy)
            .options(
                selectinload(KinesinDyneinVesicleTransportStudy.item_profiles),
                selectinload(KinesinDyneinVesicleTransportStudy.metric_traces),
            )
            .order_by(KinesinDyneinVesicleTransportStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
