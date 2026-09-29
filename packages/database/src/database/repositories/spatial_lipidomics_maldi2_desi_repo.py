"""Repository for Phase 277: Autonomous Spatial Lipidomics MALDI-2/DESI Mass Spectrometry Ionization & Fatty Acid Unsaturation Resolver."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.spatial_lipidomics_maldi2_desi import (
    SpatialLipidomicsMaldi2DesiStudy,
    SpatialLipidomicsMaldi2DesiItemProfile,
    SpatialLipidomicsMaldi2DesiMetricTrace,
)


class SpatialLipidomicsMaldi2DesiRepository:
    """Database operations for Autonomous Spatial Lipidomics MALDI-2/DESI Mass Spectrometry Ionization & Fatty Acid Unsaturation Resolver studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "spatial-lipidomics-maldi2-desi",
        lipid_species_identification_confidence: float = 97.4,
        spatial_pixel_resolution_um: float = 5.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SpatialLipidomicsMaldi2DesiStudy:
        study = SpatialLipidomicsMaldi2DesiStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            lipid_species_identification_confidence=lipid_species_identification_confidence,
            spatial_pixel_resolution_um=spatial_pixel_resolution_um,
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
    ) -> SpatialLipidomicsMaldi2DesiItemProfile:
        item = SpatialLipidomicsMaldi2DesiItemProfile(
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
    ) -> SpatialLipidomicsMaldi2DesiMetricTrace:
        item = SpatialLipidomicsMaldi2DesiMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SpatialLipidomicsMaldi2DesiStudy]:
        stmt = select(SpatialLipidomicsMaldi2DesiStudy).where(SpatialLipidomicsMaldi2DesiStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SpatialLipidomicsMaldi2DesiStudy]:
        stmt = select(SpatialLipidomicsMaldi2DesiStudy).order_by(SpatialLipidomicsMaldi2DesiStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
