"""Repository for Phase 451: Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.optical_tweezers_ribosome_translation import (
    OpticalTweezersRibosomeTranslationStudy,
    OpticalTweezersRibosomeTranslationItemProfile,
    OpticalTweezersRibosomeTranslationMetricTrace,
)


class OpticalTweezersRibosomeTranslationRepository:
    """Database operations for Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "70S Bacterial Ribosome Translating Structured mRNA Stem-Loop under Constant Force (12 pN)",
        analytical_modality: str = "ribosome-translation-dynamics",
        codon_stepping_dwell_time_ms: float = 68.4,
        mrna_unfolding_barrier_activation_energy_kb_t: float = 14.8,
        frameshift_slippage_probability: float = 0.0035,
        elongation_rate_amino_acids_per_s: float = 14.6,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OpticalTweezersRibosomeTranslationStudy:
        study = OpticalTweezersRibosomeTranslationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            codon_stepping_dwell_time_ms=codon_stepping_dwell_time_ms,
            mrna_unfolding_barrier_activation_energy_kb_t=mrna_unfolding_barrier_activation_energy_kb_t,
            frameshift_slippage_probability=frameshift_slippage_probability,
            elongation_rate_amino_acids_per_s=elongation_rate_amino_acids_per_s,
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
    ) -> OpticalTweezersRibosomeTranslationItemProfile:
        item = OpticalTweezersRibosomeTranslationItemProfile(
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
    ) -> OpticalTweezersRibosomeTranslationMetricTrace:
        trace = OpticalTweezersRibosomeTranslationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OpticalTweezersRibosomeTranslationStudy]:
        result = await self.session.execute(
            select(OpticalTweezersRibosomeTranslationStudy)
            .options(
                selectinload(OpticalTweezersRibosomeTranslationStudy.item_profiles),
                selectinload(OpticalTweezersRibosomeTranslationStudy.metric_traces),
            )
            .where(OpticalTweezersRibosomeTranslationStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[OpticalTweezersRibosomeTranslationStudy]:
        result = await self.session.execute(
            select(OpticalTweezersRibosomeTranslationStudy)
            .options(
                selectinload(OpticalTweezersRibosomeTranslationStudy.item_profiles),
                selectinload(OpticalTweezersRibosomeTranslationStudy.metric_traces),
            )
            .order_by(OpticalTweezersRibosomeTranslationStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
