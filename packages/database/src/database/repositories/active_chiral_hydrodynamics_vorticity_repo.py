"""Repository for Phase 549: Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.active_chiral_hydrodynamics_vorticity import (
    ActiveChiralHydrodynamicsVorticityStudy,
    ActiveChiralHydrodynamicsVorticityItemProfile,
    ActiveChiralHydrodynamicsVorticityMetricTrace,
)


class ActiveChiralHydrodynamicsVorticityRepository:
    """Database operations for Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Chiral Rotating Flagellated Micro-Swarm Escherichia coli in Confined Annular Microfluidic Cavities",
        analytical_modality: str = "active-chiral-hydrodynamics",
        swarming_vorticity_enstrophy_density_s2: float = 145.2,
        chiral_odd_viscosity_coefficient_pa_s: float = 0.082,
        collective_topological_circulation_rate_rad_s: float = 18.4,
        microfluidic_boundary_shear_stress_pa: float = 0.36,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> ActiveChiralHydrodynamicsVorticityStudy:
        study = ActiveChiralHydrodynamicsVorticityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            swarming_vorticity_enstrophy_density_s2=swarming_vorticity_enstrophy_density_s2,
            chiral_odd_viscosity_coefficient_pa_s=chiral_odd_viscosity_coefficient_pa_s,
            collective_topological_circulation_rate_rad_s=collective_topological_circulation_rate_rad_s,
            microfluidic_boundary_shear_stress_pa=microfluidic_boundary_shear_stress_pa,
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
    ) -> ActiveChiralHydrodynamicsVorticityItemProfile:
        item = ActiveChiralHydrodynamicsVorticityItemProfile(
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
    ) -> ActiveChiralHydrodynamicsVorticityMetricTrace:
        trace = ActiveChiralHydrodynamicsVorticityMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[ActiveChiralHydrodynamicsVorticityStudy]:
        stmt = (
            select(ActiveChiralHydrodynamicsVorticityStudy)
            .where(ActiveChiralHydrodynamicsVorticityStudy.id == study_id)
            .options(
                selectinload(ActiveChiralHydrodynamicsVorticityStudy.item_profiles),
                selectinload(ActiveChiralHydrodynamicsVorticityStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[ActiveChiralHydrodynamicsVorticityStudy]:
        stmt = (
            select(ActiveChiralHydrodynamicsVorticityStudy)
            .order_by(ActiveChiralHydrodynamicsVorticityStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(ActiveChiralHydrodynamicsVorticityStudy.item_profiles),
                selectinload(ActiveChiralHydrodynamicsVorticityStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
