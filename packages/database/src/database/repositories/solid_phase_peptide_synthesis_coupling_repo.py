"""Repository for Phase 445: Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.solid_phase_peptide_synthesis_coupling import (
    SolidPhasePeptideSynthesisStudy,
    SolidPhasePeptideSynthesisItemProfile,
    SolidPhasePeptideSynthesisMetricTrace,
)


class SolidPhasePeptideSynthesisRepository:
    """Database operations for Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "40-Mer Hydrophobic Amyloid-Beta Peptide Intermediate on Wang Resin Microbeads",
        analytical_modality: str = "solid-phase-peptide-synthesis",
        fmoc_deprotection_efficiency_ratio: float = 0.994,
        coupling_reaction_half_life_seconds: float = 45.2,
        aggregation_beta_sheet_propensity: float = 0.285,
        purity_crude_hplc_percentage: float = 94.6,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SolidPhasePeptideSynthesisStudy:
        study = SolidPhasePeptideSynthesisStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            fmoc_deprotection_efficiency_ratio=fmoc_deprotection_efficiency_ratio,
            coupling_reaction_half_life_seconds=coupling_reaction_half_life_seconds,
            aggregation_beta_sheet_propensity=aggregation_beta_sheet_propensity,
            purity_crude_hplc_percentage=purity_crude_hplc_percentage,
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
    ) -> SolidPhasePeptideSynthesisItemProfile:
        item = SolidPhasePeptideSynthesisItemProfile(
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
    ) -> SolidPhasePeptideSynthesisMetricTrace:
        trace = SolidPhasePeptideSynthesisMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SolidPhasePeptideSynthesisStudy]:
        result = await self.session.execute(
            select(SolidPhasePeptideSynthesisStudy)
            .options(
                selectinload(SolidPhasePeptideSynthesisStudy.item_profiles),
                selectinload(SolidPhasePeptideSynthesisStudy.metric_traces),
            )
            .where(SolidPhasePeptideSynthesisStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SolidPhasePeptideSynthesisStudy]:
        result = await self.session.execute(
            select(SolidPhasePeptideSynthesisStudy)
            .options(
                selectinload(SolidPhasePeptideSynthesisStudy.item_profiles),
                selectinload(SolidPhasePeptideSynthesisStudy.metric_traces),
            )
            .order_by(SolidPhasePeptideSynthesisStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
