"""Repository for Phase 479: Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.photoactivatable_cre_lineage_tracker import (
    PhotoactivatableCreLineageTrackerStudy,
    PhotoactivatableCreLineageTrackerItemProfile,
    PhotoactivatableCreLineageTrackerMetricTrace,
)


class PhotoactivatableCreLineageTrackerRepository:
    """Database operations for Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Split Magnet-Cre Recombinase Knock-In Neural Crest Stem Cell Line with LoxP Barcode Cassette",
        analytical_modality: str = "photoactivatable-cre-lineage-tracking",
        photoinduction_recombination_efficiency: float = 0.925,
        dark_state_leakage_recombination_rate: float = 0.0012,
        spatial_focal_lineage_resolution_um: float = 1.25,
        clonal_barcode_diversity_entropy: float = 8.45,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PhotoactivatableCreLineageTrackerStudy:
        study = PhotoactivatableCreLineageTrackerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            photoinduction_recombination_efficiency=photoinduction_recombination_efficiency,
            dark_state_leakage_recombination_rate=dark_state_leakage_recombination_rate,
            spatial_focal_lineage_resolution_um=spatial_focal_lineage_resolution_um,
            clonal_barcode_diversity_entropy=clonal_barcode_diversity_entropy,
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
    ) -> PhotoactivatableCreLineageTrackerItemProfile:
        item = PhotoactivatableCreLineageTrackerItemProfile(
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
    ) -> PhotoactivatableCreLineageTrackerMetricTrace:
        trace = PhotoactivatableCreLineageTrackerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PhotoactivatableCreLineageTrackerStudy]:
        result = await self.session.execute(
            select(PhotoactivatableCreLineageTrackerStudy)
            .options(
                selectinload(PhotoactivatableCreLineageTrackerStudy.item_profiles),
                selectinload(PhotoactivatableCreLineageTrackerStudy.metric_traces),
            )
            .where(PhotoactivatableCreLineageTrackerStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[PhotoactivatableCreLineageTrackerStudy]:
        result = await self.session.execute(
            select(PhotoactivatableCreLineageTrackerStudy)
            .options(
                selectinload(PhotoactivatableCreLineageTrackerStudy.item_profiles),
                selectinload(PhotoactivatableCreLineageTrackerStudy.metric_traces),
            )
            .order_by(PhotoactivatableCreLineageTrackerStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
