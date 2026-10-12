"""Repository for Phase 431: Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.spatial_transcriptomics_niche_deconvolution import (
    SpatialTranscriptomicsNicheDeconvolutionStudy,
    SpatialTranscriptomicsNicheDeconvolutionItemProfile,
    SpatialTranscriptomicsNicheDeconvolutionMetricTrace,
)


class SpatialTranscriptomicsNicheDeconvolutionRepository:
    """Database operations for Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "10x Visium HD Formalin-Fixed Paraffin-Embedded Tissue Slice",
        analytical_modality: str = "spatial-niche-deconvolution",
        sub_spot_cell_type_purity: float = 0.942,
        niche_cross_talk_significance_p: float = 0.0008,
        ligand_receptor_spatial_correlation: float = 0.865,
        microenvironment_entropy_index: float = 1.42,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SpatialTranscriptomicsNicheDeconvolutionStudy:
        study = SpatialTranscriptomicsNicheDeconvolutionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            sub_spot_cell_type_purity=sub_spot_cell_type_purity,
            niche_cross_talk_significance_p=niche_cross_talk_significance_p,
            ligand_receptor_spatial_correlation=ligand_receptor_spatial_correlation,
            microenvironment_entropy_index=microenvironment_entropy_index,
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
    ) -> SpatialTranscriptomicsNicheDeconvolutionItemProfile:
        item = SpatialTranscriptomicsNicheDeconvolutionItemProfile(
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
    ) -> SpatialTranscriptomicsNicheDeconvolutionMetricTrace:
        trace = SpatialTranscriptomicsNicheDeconvolutionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SpatialTranscriptomicsNicheDeconvolutionStudy]:
        result = await self.session.execute(
            select(SpatialTranscriptomicsNicheDeconvolutionStudy)
            .options(
                selectinload(SpatialTranscriptomicsNicheDeconvolutionStudy.item_profiles),
                selectinload(SpatialTranscriptomicsNicheDeconvolutionStudy.metric_traces),
            )
            .where(SpatialTranscriptomicsNicheDeconvolutionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SpatialTranscriptomicsNicheDeconvolutionStudy]:
        result = await self.session.execute(
            select(SpatialTranscriptomicsNicheDeconvolutionStudy)
            .options(
                selectinload(SpatialTranscriptomicsNicheDeconvolutionStudy.item_profiles),
                selectinload(SpatialTranscriptomicsNicheDeconvolutionStudy.metric_traces),
            )
            .order_by(SpatialTranscriptomicsNicheDeconvolutionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
