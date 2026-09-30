"""Repository for Phase 414: Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryo_fib_milling import (
    CryoFibMillingStudy,
    CryoFibMillingItemProfile,
    CryoFibMillingMetricTrace,
)


from sqlalchemy.orm import selectinload


class CryoFibMillingRepository:
    """Database operations for Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitreous Cellular Cryo-Lamella",
        analytical_modality: str = "cryo-fib-milling",
        in_situ_lamella_thickness_nm: float = 112.5,
        curtaining_artifact_suppression_ratio: float = 0.948,
        gallium_ion_beam_current_pA: float = 30.0,
        vitreous_ice_preservation_score: float = 0.982,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoFibMillingStudy:
        study = CryoFibMillingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            in_situ_lamella_thickness_nm=in_situ_lamella_thickness_nm,
            curtaining_artifact_suppression_ratio=curtaining_artifact_suppression_ratio,
            gallium_ion_beam_current_pA=gallium_ion_beam_current_pA,
            vitreous_ice_preservation_score=vitreous_ice_preservation_score,
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
        profile_category: str = "Milling Stage",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> CryoFibMillingItemProfile:
        item = CryoFibMillingItemProfile(
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
    ) -> CryoFibMillingMetricTrace:
        trace = CryoFibMillingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoFibMillingStudy]:
        result = await self.session.execute(
            select(CryoFibMillingStudy)
            .options(
                selectinload(CryoFibMillingStudy.item_profiles),
                selectinload(CryoFibMillingStudy.metric_traces),
            )
            .where(CryoFibMillingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryoFibMillingStudy]:
        result = await self.session.execute(
            select(CryoFibMillingStudy)
            .options(
                selectinload(CryoFibMillingStudy.item_profiles),
                selectinload(CryoFibMillingStudy.metric_traces),
            )
            .order_by(CryoFibMillingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
