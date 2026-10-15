"""Repository for Phase 535: Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_epigenetic_crispr_memory_cascade import (
    SyntheticEpigeneticCrisprMemoryCascadeStudy,
    SyntheticEpigeneticCrisprMemoryCascadeItemProfile,
    SyntheticEpigeneticCrisprMemoryCascadeMetricTrace,
)


class SyntheticEpigeneticCrisprMemoryCascadeRepository:
    """Database operations for Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered dCas9-KRAB-MeCP2 & dCas9-TET1 Autocatalytic Feedback Toggle in Human iPSCs",
        analytical_modality: str = "crispr-epigenetic-memory-cascade",
        transcriptional_repression_half_life_days: float = 42.0,
        h3k9me3_deposition_spreading_kb: float = 4.8,
        epigenetic_memory_heritability_generations: float = 35.0,
        reversible_reactivation_efficiency_pct: float = 94.5,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticEpigeneticCrisprMemoryCascadeStudy:
        study = SyntheticEpigeneticCrisprMemoryCascadeStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            transcriptional_repression_half_life_days=transcriptional_repression_half_life_days,
            h3k9me3_deposition_spreading_kb=h3k9me3_deposition_spreading_kb,
            epigenetic_memory_heritability_generations=epigenetic_memory_heritability_generations,
            reversible_reactivation_efficiency_pct=reversible_reactivation_efficiency_pct,
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
    ) -> SyntheticEpigeneticCrisprMemoryCascadeItemProfile:
        item = SyntheticEpigeneticCrisprMemoryCascadeItemProfile(
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
    ) -> SyntheticEpigeneticCrisprMemoryCascadeMetricTrace:
        trace = SyntheticEpigeneticCrisprMemoryCascadeMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticEpigeneticCrisprMemoryCascadeStudy]:
        stmt = (
            select(SyntheticEpigeneticCrisprMemoryCascadeStudy)
            .where(SyntheticEpigeneticCrisprMemoryCascadeStudy.id == study_id)
            .options(
                selectinload(SyntheticEpigeneticCrisprMemoryCascadeStudy.item_profiles),
                selectinload(SyntheticEpigeneticCrisprMemoryCascadeStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SyntheticEpigeneticCrisprMemoryCascadeStudy]:
        stmt = (
            select(SyntheticEpigeneticCrisprMemoryCascadeStudy)
            .order_by(SyntheticEpigeneticCrisprMemoryCascadeStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SyntheticEpigeneticCrisprMemoryCascadeStudy.item_profiles),
                selectinload(SyntheticEpigeneticCrisprMemoryCascadeStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
