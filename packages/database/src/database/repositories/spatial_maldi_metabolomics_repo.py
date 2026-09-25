"""Repository for Phase 188: Spatial Metabolomics MALDI-MSI Tissue Architecture Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.spatial_maldi_metabolomics import (
    SpatialMaldiMetabolomicsStudy,
    SpatialMaldiMetabolomicsItemProfile,
    SpatialMaldiMetabolomicsMetricTrace,
)


class SpatialMaldiMetabolomicsRepository:
    """Database operations for Spatial Metabolomics MALDI-MSI Tissue Architecture Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "Spatial Metabolomics MALDI-MSI",
        spatial_resolution_microns: float = 20.0,
        metabolic_heterogeneity_index: float = 0.874,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SpatialMaldiMetabolomicsStudy:
        study = SpatialMaldiMetabolomicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            spatial_resolution_microns=spatial_resolution_microns,
            metabolic_heterogeneity_index=metabolic_heterogeneity_index,
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
    ) -> SpatialMaldiMetabolomicsItemProfile:
        item = SpatialMaldiMetabolomicsItemProfile(
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
    ) -> SpatialMaldiMetabolomicsMetricTrace:
        item = SpatialMaldiMetabolomicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SpatialMaldiMetabolomicsStudy]:
        stmt = select(SpatialMaldiMetabolomicsStudy).where(SpatialMaldiMetabolomicsStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SpatialMaldiMetabolomicsStudy]:
        stmt = select(SpatialMaldiMetabolomicsStudy).order_by(SpatialMaldiMetabolomicsStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
