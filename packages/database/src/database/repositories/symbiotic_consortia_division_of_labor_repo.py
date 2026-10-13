"""Repository for Phase 464: Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.symbiotic_consortia_division_of_labor import (
    SymbioticConsortiaDivisionOfLaborStudy,
    SymbioticConsortiaDivisionOfLaborItemProfile,
    SymbioticConsortiaDivisionOfLaborMetricTrace,
)


class SymbioticConsortiaDivisionOfLaborRepository:
    """Database operations for Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered E. coli and S. cerevisiae Cross-Feeding Co-Culture in Chemostat Bioreactor",
        analytical_modality: str = "symbiotic-metabolic-labor-dynamics",
        chemostat_steady_state_biomass_ratio: float = 1.15,
        cross_feeding_metabolite_exchange_flux_mmol_g_hr: float = 6.85,
        population_coexistence_lyapunov_exponent: float = -0.42,
        resource_utilization_synergy_factor: float = 1.85,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SymbioticConsortiaDivisionOfLaborStudy:
        study = SymbioticConsortiaDivisionOfLaborStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            chemostat_steady_state_biomass_ratio=chemostat_steady_state_biomass_ratio,
            cross_feeding_metabolite_exchange_flux_mmol_g_hr=cross_feeding_metabolite_exchange_flux_mmol_g_hr,
            population_coexistence_lyapunov_exponent=population_coexistence_lyapunov_exponent,
            resource_utilization_synergy_factor=resource_utilization_synergy_factor,
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
    ) -> SymbioticConsortiaDivisionOfLaborItemProfile:
        item = SymbioticConsortiaDivisionOfLaborItemProfile(
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
    ) -> SymbioticConsortiaDivisionOfLaborMetricTrace:
        trace = SymbioticConsortiaDivisionOfLaborMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SymbioticConsortiaDivisionOfLaborStudy]:
        result = await self.session.execute(
            select(SymbioticConsortiaDivisionOfLaborStudy)
            .options(
                selectinload(SymbioticConsortiaDivisionOfLaborStudy.item_profiles),
                selectinload(SymbioticConsortiaDivisionOfLaborStudy.metric_traces),
            )
            .where(SymbioticConsortiaDivisionOfLaborStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SymbioticConsortiaDivisionOfLaborStudy]:
        result = await self.session.execute(
            select(SymbioticConsortiaDivisionOfLaborStudy)
            .options(
                selectinload(SymbioticConsortiaDivisionOfLaborStudy.item_profiles),
                selectinload(SymbioticConsortiaDivisionOfLaborStudy.metric_traces),
            )
            .order_by(SymbioticConsortiaDivisionOfLaborStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
