"""Repository for Phase 402: Liquid Biopsy ctDNA Methylation & Tissue-of-Origin Deconvolver."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.circulating_tumor_dna_methylation import (
    CirculatingTumorDnaMethylationStudy,
    CirculatingTumorDnaMethylationItemProfile,
    CirculatingTumorDnaMethylationMetricTrace,
)


class CirculatingTumorDnaMethylationRepository:
    """Database operations for Liquid Biopsy ctDNA Methylation & Tissue-of-Origin Deconvolver."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "liquid-biopsy-ctdna-methylation",
        tissue_of_origin_classification_accuracy_pct: float = 96.8,
        ctdna_limit_of_detection_allele_fraction_ppm: float = 8.5,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CirculatingTumorDnaMethylationStudy:
        study = CirculatingTumorDnaMethylationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            tissue_of_origin_classification_accuracy_pct=tissue_of_origin_classification_accuracy_pct,
            ctdna_limit_of_detection_allele_fraction_ppm=ctdna_limit_of_detection_allele_fraction_ppm,
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
    ) -> CirculatingTumorDnaMethylationItemProfile:
        item = CirculatingTumorDnaMethylationItemProfile(
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
    ) -> CirculatingTumorDnaMethylationMetricTrace:
        item = CirculatingTumorDnaMethylationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CirculatingTumorDnaMethylationStudy]:
        stmt = select(CirculatingTumorDnaMethylationStudy).where(CirculatingTumorDnaMethylationStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CirculatingTumorDnaMethylationStudy]:
        stmt = select(CirculatingTumorDnaMethylationStudy).order_by(CirculatingTumorDnaMethylationStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
