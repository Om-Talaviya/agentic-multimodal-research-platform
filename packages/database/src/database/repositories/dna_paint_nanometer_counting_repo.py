"""Repository for Phase 421: Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.dna_paint_nanometer_counting import (
    DnaPaintNanometerCountingStudy,
    DnaPaintNanometerCountingItemProfile,
    DnaPaintNanometerCountingMetricTrace,
)


class DnaPaintNanometerCountingRepository:
    """Database operations for Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Nuclear Pore Complex Scaffold with Fluorescent Imager Strands",
        analytical_modality: str = "dna-paint-counting",
        spatial_localization_precision_nm: float = 3.15,
        absolute_molecule_count: float = 32.0,
        qpaint_binding_frequency_hz: float = 0.42,
        background_dark_time_ratio: float = 0.978,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DnaPaintNanometerCountingStudy:
        study = DnaPaintNanometerCountingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            spatial_localization_precision_nm=spatial_localization_precision_nm,
            absolute_molecule_count=absolute_molecule_count,
            qpaint_binding_frequency_hz=qpaint_binding_frequency_hz,
            background_dark_time_ratio=background_dark_time_ratio,
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
    ) -> DnaPaintNanometerCountingItemProfile:
        item = DnaPaintNanometerCountingItemProfile(
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
    ) -> DnaPaintNanometerCountingMetricTrace:
        trace = DnaPaintNanometerCountingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DnaPaintNanometerCountingStudy]:
        result = await self.session.execute(
            select(DnaPaintNanometerCountingStudy)
            .options(
                selectinload(DnaPaintNanometerCountingStudy.item_profiles),
                selectinload(DnaPaintNanometerCountingStudy.metric_traces),
            )
            .where(DnaPaintNanometerCountingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DnaPaintNanometerCountingStudy]:
        result = await self.session.execute(
            select(DnaPaintNanometerCountingStudy)
            .options(
                selectinload(DnaPaintNanometerCountingStudy.item_profiles),
                selectinload(DnaPaintNanometerCountingStudy.metric_traces),
            )
            .order_by(DnaPaintNanometerCountingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
