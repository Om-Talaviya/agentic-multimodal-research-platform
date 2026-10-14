"""Repository for Phase 480: Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.guv_electroformation_dynamics import (
    GuvElectroformationDynamicsStudy,
    GuvElectroformationDynamicsItemProfile,
    GuvElectroformationDynamicsMetricTrace,
)


class GuvElectroformationDynamicsRepository:
    """Database operations for Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Indium Tin Oxide (ITO) Microelectrode Chamber with POPC/Cholesterol Bilayer Hydration",
        analytical_modality: str = "guv-electroformation-dynamics",
        guv_mean_diameter_yield_um: float = 28.5,
        bilayer_bending_rigidity_kbT: float = 22.4,
        electric_field_interfacial_shear_V_per_m: float = 1200.0,
        unilamellarity_monodispersity_cv: float = 0.065,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> GuvElectroformationDynamicsStudy:
        study = GuvElectroformationDynamicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            guv_mean_diameter_yield_um=guv_mean_diameter_yield_um,
            bilayer_bending_rigidity_kbT=bilayer_bending_rigidity_kbT,
            electric_field_interfacial_shear_V_per_m=electric_field_interfacial_shear_V_per_m,
            unilamellarity_monodispersity_cv=unilamellarity_monodispersity_cv,
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
    ) -> GuvElectroformationDynamicsItemProfile:
        item = GuvElectroformationDynamicsItemProfile(
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
    ) -> GuvElectroformationDynamicsMetricTrace:
        trace = GuvElectroformationDynamicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[GuvElectroformationDynamicsStudy]:
        result = await self.session.execute(
            select(GuvElectroformationDynamicsStudy)
            .options(
                selectinload(GuvElectroformationDynamicsStudy.item_profiles),
                selectinload(GuvElectroformationDynamicsStudy.metric_traces),
            )
            .where(GuvElectroformationDynamicsStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[GuvElectroformationDynamicsStudy]:
        result = await self.session.execute(
            select(GuvElectroformationDynamicsStudy)
            .options(
                selectinload(GuvElectroformationDynamicsStudy.item_profiles),
                selectinload(GuvElectroformationDynamicsStudy.metric_traces),
            )
            .order_by(GuvElectroformationDynamicsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
