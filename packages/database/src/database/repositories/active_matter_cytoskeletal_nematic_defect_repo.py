"""Repository for Phase 519: Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.active_matter_cytoskeletal_nematic_defect import (
    ActiveMatterCytoskeletalNematicDefectStudy,
    ActiveMatterCytoskeletalNematicDefectItemProfile,
    ActiveMatterCytoskeletalNematicDefectMetricTrace,
)


class ActiveMatterCytoskeletalNematicDefectRepository:
    """Database operations for Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Microtubule-Kinesin Active Gel Nematic Liquid Crystal Layer at Oil-Water Interface",
        analytical_modality: str = "active-nematic-matter-dynamics",
        topological_defect_annihilation_rate_s_inv: float = 0.45,
        active_turbulent_vortex_correlation_length_um: float = 18.5,
        plus_half_defect_self_propulsion_velocity_um_per_s: float = 4.8,
        atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3: float = 12.4,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> ActiveMatterCytoskeletalNematicDefectStudy:
        study = ActiveMatterCytoskeletalNematicDefectStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            topological_defect_annihilation_rate_s_inv=topological_defect_annihilation_rate_s_inv,
            active_turbulent_vortex_correlation_length_um=active_turbulent_vortex_correlation_length_um,
            plus_half_defect_self_propulsion_velocity_um_per_s=plus_half_defect_self_propulsion_velocity_um_per_s,
            atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3=atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3,
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
    ) -> ActiveMatterCytoskeletalNematicDefectItemProfile:
        item = ActiveMatterCytoskeletalNematicDefectItemProfile(
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
    ) -> ActiveMatterCytoskeletalNematicDefectMetricTrace:
        trace = ActiveMatterCytoskeletalNematicDefectMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[ActiveMatterCytoskeletalNematicDefectStudy]:
        result = await self.session.execute(
            select(ActiveMatterCytoskeletalNematicDefectStudy)
            .options(
                selectinload(ActiveMatterCytoskeletalNematicDefectStudy.item_profiles),
                selectinload(ActiveMatterCytoskeletalNematicDefectStudy.metric_traces),
            )
            .where(ActiveMatterCytoskeletalNematicDefectStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[ActiveMatterCytoskeletalNematicDefectStudy]:
        result = await self.session.execute(
            select(ActiveMatterCytoskeletalNematicDefectStudy)
            .options(
                selectinload(ActiveMatterCytoskeletalNematicDefectStudy.item_profiles),
                selectinload(ActiveMatterCytoskeletalNematicDefectStudy.metric_traces),
            )
            .order_by(ActiveMatterCytoskeletalNematicDefectStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
