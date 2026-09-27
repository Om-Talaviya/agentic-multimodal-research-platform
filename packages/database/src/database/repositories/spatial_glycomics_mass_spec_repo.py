"""Repository for Phase 240: Autonomous Spatial MALDI-MSI Glycan Branching & Sialylation Tissue Micro-Architecture Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.spatial_glycomics_mass_spec import (
    SpatialGlycomicsMassSpecStudy,
    SpatialGlycomicsMassSpecItemProfile,
    SpatialGlycomicsMassSpecMetricTrace,
)


class SpatialGlycomicsMassSpecRepository:
    """Database operations for Autonomous Spatial MALDI-MSI Glycan Branching & Sialylation Tissue Micro-Architecture Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "spatial-glycomics-mass-spec",
        glycan_isomer_resolution_score: float = 98.4,
        core_fucosylation_intensity_ratio: float = 4.6,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SpatialGlycomicsMassSpecStudy:
        study = SpatialGlycomicsMassSpecStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            glycan_isomer_resolution_score=glycan_isomer_resolution_score,
            core_fucosylation_intensity_ratio=core_fucosylation_intensity_ratio,
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
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> SpatialGlycomicsMassSpecItemProfile:
        item = SpatialGlycomicsMassSpecItemProfile(
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
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> SpatialGlycomicsMassSpecMetricTrace:
        item = SpatialGlycomicsMassSpecMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[SpatialGlycomicsMassSpecStudy]:
        stmt = select(SpatialGlycomicsMassSpecStudy).where(SpatialGlycomicsMassSpecStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SpatialGlycomicsMassSpecStudy]:
        stmt = select(SpatialGlycomicsMassSpecStudy).order_by(SpatialGlycomicsMassSpecStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
