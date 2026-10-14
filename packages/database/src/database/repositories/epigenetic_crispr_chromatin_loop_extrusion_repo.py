"""Repository for Phase 515: Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.epigenetic_crispr_chromatin_loop_extrusion import (
    EpigeneticCrisprChromatinLoopExtrusionStudy,
    EpigeneticCrisprChromatinLoopExtrusionItemProfile,
    EpigeneticCrisprChromatinLoopExtrusionMetricTrace,
)


class EpigeneticCrisprChromatinLoopExtrusionRepository:
    """Database operations for Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human K562 Cells with Chemically Dimerizable dCas9-CTCF Targeted to MYC Super-Enhancer TAD",
        analytical_modality: str = "crispr-chromatin-loop-rewriting",
        induced_chromatin_loop_contact_frequency_enhancement: float = 4.2,
        insulation_boundary_score_gain: float = 0.825,
        target_oncogene_expression_activation_fold: float = 5.4,
        cohesin_retention_time_at_engineered_ctcf_min: float = 38.0,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> EpigeneticCrisprChromatinLoopExtrusionStudy:
        study = EpigeneticCrisprChromatinLoopExtrusionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            induced_chromatin_loop_contact_frequency_enhancement=induced_chromatin_loop_contact_frequency_enhancement,
            insulation_boundary_score_gain=insulation_boundary_score_gain,
            target_oncogene_expression_activation_fold=target_oncogene_expression_activation_fold,
            cohesin_retention_time_at_engineered_ctcf_min=cohesin_retention_time_at_engineered_ctcf_min,
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
    ) -> EpigeneticCrisprChromatinLoopExtrusionItemProfile:
        item = EpigeneticCrisprChromatinLoopExtrusionItemProfile(
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
    ) -> EpigeneticCrisprChromatinLoopExtrusionMetricTrace:
        trace = EpigeneticCrisprChromatinLoopExtrusionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[EpigeneticCrisprChromatinLoopExtrusionStudy]:
        result = await self.session.execute(
            select(EpigeneticCrisprChromatinLoopExtrusionStudy)
            .options(
                selectinload(EpigeneticCrisprChromatinLoopExtrusionStudy.item_profiles),
                selectinload(EpigeneticCrisprChromatinLoopExtrusionStudy.metric_traces),
            )
            .where(EpigeneticCrisprChromatinLoopExtrusionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[EpigeneticCrisprChromatinLoopExtrusionStudy]:
        result = await self.session.execute(
            select(EpigeneticCrisprChromatinLoopExtrusionStudy)
            .options(
                selectinload(EpigeneticCrisprChromatinLoopExtrusionStudy.item_profiles),
                selectinload(EpigeneticCrisprChromatinLoopExtrusionStudy.metric_traces),
            )
            .order_by(EpigeneticCrisprChromatinLoopExtrusionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
