"""Repository for Phase 502: Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.acoustic_droplet_single_exosome_profiler import (
    AcousticDropletSingleExosomeProfilerStudy,
    AcousticDropletSingleExosomeProfilerItemProfile,
    AcousticDropletSingleExosomeProfilerMetricTrace,
)


class AcousticDropletSingleExosomeProfilerRepository:
    """Database operations for Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Surface Acoustic Wave (SAW) Focused Patient Plasma with CD63/CD81/CD9 Fluorophore Micro-Beads",
        analytical_modality: str = "acoustic-droplet-single-exosome",
        exosome_acoustic_separation_purity_pct: float = 96.8,
        droplet_single_vesicle_encapsulation_lambda: float = 0.28,
        tetraspanin_triplet_colocalization_score: float = 0.915,
        low_abundant_cargo_detection_limit_fM: float = 15.0,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> AcousticDropletSingleExosomeProfilerStudy:
        study = AcousticDropletSingleExosomeProfilerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            exosome_acoustic_separation_purity_pct=exosome_acoustic_separation_purity_pct,
            droplet_single_vesicle_encapsulation_lambda=droplet_single_vesicle_encapsulation_lambda,
            tetraspanin_triplet_colocalization_score=tetraspanin_triplet_colocalization_score,
            low_abundant_cargo_detection_limit_fM=low_abundant_cargo_detection_limit_fM,
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
    ) -> AcousticDropletSingleExosomeProfilerItemProfile:
        item = AcousticDropletSingleExosomeProfilerItemProfile(
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
    ) -> AcousticDropletSingleExosomeProfilerMetricTrace:
        trace = AcousticDropletSingleExosomeProfilerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[AcousticDropletSingleExosomeProfilerStudy]:
        result = await self.session.execute(
            select(AcousticDropletSingleExosomeProfilerStudy)
            .options(
                selectinload(AcousticDropletSingleExosomeProfilerStudy.item_profiles),
                selectinload(AcousticDropletSingleExosomeProfilerStudy.metric_traces),
            )
            .where(AcousticDropletSingleExosomeProfilerStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[AcousticDropletSingleExosomeProfilerStudy]:
        result = await self.session.execute(
            select(AcousticDropletSingleExosomeProfilerStudy)
            .options(
                selectinload(AcousticDropletSingleExosomeProfilerStudy.item_profiles),
                selectinload(AcousticDropletSingleExosomeProfilerStudy.metric_traces),
            )
            .order_by(AcousticDropletSingleExosomeProfilerStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
