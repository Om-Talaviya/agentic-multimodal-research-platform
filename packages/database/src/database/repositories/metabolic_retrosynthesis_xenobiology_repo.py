"""Repository for Phase 507: Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.metabolic_retrosynthesis_xenobiology import (
    MetabolicRetrosynthesisXenobiologyStudy,
    MetabolicRetrosynthesisXenobiologyItemProfile,
    MetabolicRetrosynthesisXenobiologyMetricTrace,
)


class MetabolicRetrosynthesisXenobiologyRepository:
    """Database operations for Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes",
        analytical_modality: str = "xenobiotic-retrosynthesis-flux",
        retrosynthetic_pathway_plausibility_score: float = 0.942,
        thermodynamic_driving_force_delta_G_kj_mol: float = -34.8,
        theoretical_maximum_carbon_yield_pct: float = 92.5,
        chassis_endogenous_flux_perturbation_index: float = 0.125,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MetabolicRetrosynthesisXenobiologyStudy:
        study = MetabolicRetrosynthesisXenobiologyStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            retrosynthetic_pathway_plausibility_score=retrosynthetic_pathway_plausibility_score,
            thermodynamic_driving_force_delta_G_kj_mol=thermodynamic_driving_force_delta_G_kj_mol,
            theoretical_maximum_carbon_yield_pct=theoretical_maximum_carbon_yield_pct,
            chassis_endogenous_flux_perturbation_index=chassis_endogenous_flux_perturbation_index,
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
    ) -> MetabolicRetrosynthesisXenobiologyItemProfile:
        item = MetabolicRetrosynthesisXenobiologyItemProfile(
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
    ) -> MetabolicRetrosynthesisXenobiologyMetricTrace:
        trace = MetabolicRetrosynthesisXenobiologyMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MetabolicRetrosynthesisXenobiologyStudy]:
        result = await self.session.execute(
            select(MetabolicRetrosynthesisXenobiologyStudy)
            .options(
                selectinload(MetabolicRetrosynthesisXenobiologyStudy.item_profiles),
                selectinload(MetabolicRetrosynthesisXenobiologyStudy.metric_traces),
            )
            .where(MetabolicRetrosynthesisXenobiologyStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MetabolicRetrosynthesisXenobiologyStudy]:
        result = await self.session.execute(
            select(MetabolicRetrosynthesisXenobiologyStudy)
            .options(
                selectinload(MetabolicRetrosynthesisXenobiologyStudy.item_profiles),
                selectinload(MetabolicRetrosynthesisXenobiologyStudy.metric_traces),
            )
            .order_by(MetabolicRetrosynthesisXenobiologyStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
