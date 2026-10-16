"""Repository for Phase 571: Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_cell_spatial_epigenomic_cut_and_tag import (
    SingleCellSpatialEpigenomicCutAndTagStudy,
    SingleCellSpatialEpigenomicCutAndTagItemProfile,
    SingleCellSpatialEpigenomicCutAndTagMetricTrace,
)


class SingleCellSpatialEpigenomicCutAndTagRepository:
    """Repository for Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        chromatin_enrichment_specificity: float,
        spatial_barcoding_purity: float,
        signal_to_background_promoter_ratio: float,
        niche_clustering_silhouette: float,
        confidence_score: float = 0.994,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> SingleCellSpatialEpigenomicCutAndTagStudy:
        study = SingleCellSpatialEpigenomicCutAndTagStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            chromatin_enrichment_specificity=chromatin_enrichment_specificity,
            spatial_barcoding_purity=spatial_barcoding_purity,
            signal_to_background_promoter_ratio=signal_to_background_promoter_ratio,
            niche_clustering_silhouette=niche_clustering_silhouette,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[SingleCellSpatialEpigenomicCutAndTagStudy]:
        stmt = select(SingleCellSpatialEpigenomicCutAndTagStudy).where(SingleCellSpatialEpigenomicCutAndTagStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SingleCellSpatialEpigenomicCutAndTagStudy]:
        stmt = select(SingleCellSpatialEpigenomicCutAndTagStudy).order_by(SingleCellSpatialEpigenomicCutAndTagStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        quantitative_value: float,
        profile_category: str = "Analysis Profile",
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> SingleCellSpatialEpigenomicCutAndTagItemProfile:
        profile = SingleCellSpatialEpigenomicCutAndTagItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> SingleCellSpatialEpigenomicCutAndTagMetricTrace:
        trace = SingleCellSpatialEpigenomicCutAndTagMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace
