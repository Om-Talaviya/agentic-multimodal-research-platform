"""Repository for Phase 478: Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.nanopore_dna_methylation_discrimination import (
    NanoporeDnaMethylationDiscriminationStudy,
    NanoporeDnaMethylationDiscriminationItemProfile,
    NanoporeDnaMethylationDiscriminationMetricTrace,
)


class NanoporeDnaMethylationDiscriminationRepository:
    """Database operations for Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Sub-2nm Si3N4 Nanopore Translocating Native Synthetic 5mC / 5hmC Epigenetic DNA Duplexes",
        analytical_modality: str = "nanopore-methylation-discrimination",
        fractional_current_blockade_ratio: float = 0.842,
        epigenetic_base_dwell_time_us: float = 18.5,
        five_mc_vs_unmethylated_snr_db: float = 14.8,
        single_base_resolution_confidence: float = 0.988,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NanoporeDnaMethylationDiscriminationStudy:
        study = NanoporeDnaMethylationDiscriminationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            fractional_current_blockade_ratio=fractional_current_blockade_ratio,
            epigenetic_base_dwell_time_us=epigenetic_base_dwell_time_us,
            five_mc_vs_unmethylated_snr_db=five_mc_vs_unmethylated_snr_db,
            single_base_resolution_confidence=single_base_resolution_confidence,
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
    ) -> NanoporeDnaMethylationDiscriminationItemProfile:
        item = NanoporeDnaMethylationDiscriminationItemProfile(
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
    ) -> NanoporeDnaMethylationDiscriminationMetricTrace:
        trace = NanoporeDnaMethylationDiscriminationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NanoporeDnaMethylationDiscriminationStudy]:
        result = await self.session.execute(
            select(NanoporeDnaMethylationDiscriminationStudy)
            .options(
                selectinload(NanoporeDnaMethylationDiscriminationStudy.item_profiles),
                selectinload(NanoporeDnaMethylationDiscriminationStudy.metric_traces),
            )
            .where(NanoporeDnaMethylationDiscriminationStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[NanoporeDnaMethylationDiscriminationStudy]:
        result = await self.session.execute(
            select(NanoporeDnaMethylationDiscriminationStudy)
            .options(
                selectinload(NanoporeDnaMethylationDiscriminationStudy.item_profiles),
                selectinload(NanoporeDnaMethylationDiscriminationStudy.metric_traces),
            )
            .order_by(NanoporeDnaMethylationDiscriminationStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
