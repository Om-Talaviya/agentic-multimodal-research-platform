"""Repository for Phase 566: Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.rna_targeted_adar_deaminase_editing import (
    RnaTargetedAdarDeaminaseEditingStudy,
    RnaTargetedAdarDeaminaseEditingItemProfile,
    RnaTargetedAdarDeaminaseEditingMetricTrace,
)


class RnaTargetedAdarDeaminaseEditingRepository:
    """Database operations for Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Endogenous Human ADAR2 Deaminase recruited via Circular Guide RNA (arRNA) targeting Premature Stop Codons in MECP2 mRNA",
        analytical_modality: str = "programmable-adar-rna-editing",
        targeted_adenosine_to_inosine_editing_efficiency_pct: float = 78.4,
        bystander_adenosine_deamination_rate_pct: float = 2.1,
        guide_circular_rna_stability_half_life_hours: float = 48.0,
        target_transcript_restoration_fold: float = 12.5,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> RnaTargetedAdarDeaminaseEditingStudy:
        study = RnaTargetedAdarDeaminaseEditingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            targeted_adenosine_to_inosine_editing_efficiency_pct=targeted_adenosine_to_inosine_editing_efficiency_pct,
            bystander_adenosine_deamination_rate_pct=bystander_adenosine_deamination_rate_pct,
            guide_circular_rna_stability_half_life_hours=guide_circular_rna_stability_half_life_hours,
            target_transcript_restoration_fold=target_transcript_restoration_fold,
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
    ) -> RnaTargetedAdarDeaminaseEditingItemProfile:
        item = RnaTargetedAdarDeaminaseEditingItemProfile(
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
    ) -> RnaTargetedAdarDeaminaseEditingMetricTrace:
        trace = RnaTargetedAdarDeaminaseEditingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[RnaTargetedAdarDeaminaseEditingStudy]:
        stmt = (
            select(RnaTargetedAdarDeaminaseEditingStudy)
            .where(RnaTargetedAdarDeaminaseEditingStudy.id == study_id)
            .options(
                selectinload(RnaTargetedAdarDeaminaseEditingStudy.item_profiles),
                selectinload(RnaTargetedAdarDeaminaseEditingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[RnaTargetedAdarDeaminaseEditingStudy]:
        stmt = (
            select(RnaTargetedAdarDeaminaseEditingStudy)
            .order_by(RnaTargetedAdarDeaminaseEditingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(RnaTargetedAdarDeaminaseEditingStudy.item_profiles),
                selectinload(RnaTargetedAdarDeaminaseEditingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
