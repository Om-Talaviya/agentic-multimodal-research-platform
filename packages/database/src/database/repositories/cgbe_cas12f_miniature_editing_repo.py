"""Repository for Phase 427: Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cgbe_cas12f_miniature_editing import (
    CgbeCas12fMiniatureEditingStudy,
    CgbeCas12fMiniatureEditingItemProfile,
    CgbeCas12fMiniatureEditingMetricTrace,
)


class CgbeCas12fMiniatureEditingRepository:
    """Database operations for Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Ultra-Compact Cas12f Miniature CGBE Complex in AAV Vector",
        analytical_modality: str = "cgbe-cas12f-editing",
        c_to_g_conversion_purity_percent: float = 88.6,
        on_target_indel_frequency_percent: float = 2.1,
        aav_packaging_size_kb: float = 4.25,
        off_target_cleavage_fraction: float = 0.0035,
        confidence_score: float = 0.987,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CgbeCas12fMiniatureEditingStudy:
        study = CgbeCas12fMiniatureEditingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            c_to_g_conversion_purity_percent=c_to_g_conversion_purity_percent,
            on_target_indel_frequency_percent=on_target_indel_frequency_percent,
            aav_packaging_size_kb=aav_packaging_size_kb,
            off_target_cleavage_fraction=off_target_cleavage_fraction,
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
    ) -> CgbeCas12fMiniatureEditingItemProfile:
        item = CgbeCas12fMiniatureEditingItemProfile(
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
    ) -> CgbeCas12fMiniatureEditingMetricTrace:
        trace = CgbeCas12fMiniatureEditingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CgbeCas12fMiniatureEditingStudy]:
        result = await self.session.execute(
            select(CgbeCas12fMiniatureEditingStudy)
            .options(
                selectinload(CgbeCas12fMiniatureEditingStudy.item_profiles),
                selectinload(CgbeCas12fMiniatureEditingStudy.metric_traces),
            )
            .where(CgbeCas12fMiniatureEditingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CgbeCas12fMiniatureEditingStudy]:
        result = await self.session.execute(
            select(CgbeCas12fMiniatureEditingStudy)
            .options(
                selectinload(CgbeCas12fMiniatureEditingStudy.item_profiles),
                selectinload(CgbeCas12fMiniatureEditingStudy.metric_traces),
            )
            .order_by(CgbeCas12fMiniatureEditingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
