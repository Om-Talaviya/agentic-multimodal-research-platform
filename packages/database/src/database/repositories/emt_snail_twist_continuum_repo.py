"""Repository for Phase 489: Autonomous Multicellular Epithelial-to-Mesenchymal Transition (EMT) Snail-Twist Continuum Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.emt_snail_twist_continuum import (
    EmtSnailTwistContinuumStudy,
    EmtSnailTwistContinuumItemProfile,
    EmtSnailTwistContinuumMetricTrace,
)


class EmtSnailTwistContinuumRepository:
    """Database operations for Autonomous Multicellular Epithelial-to-Mesenchymal Transition (EMT) Snail-Twist Continuum Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "TGF-beta Stimulated Mammary Epithelial MCF-10A Monolayer with Fluorescent E-Cadherin / Vimentin",
        analytical_modality: str = "emt-snail-twist-continuum",
        e_cadherin_vimentin_expression_ratio: float = 0.42,
        intermediate_hybrid_state_fraction: float = 0.38,
        snail1_nuclear_translocation_tau_hours: float = 14.5,
        mesenchymal_migration_velocity_um_per_hr: float = 24.8,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> EmtSnailTwistContinuumStudy:
        study = EmtSnailTwistContinuumStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            e_cadherin_vimentin_expression_ratio=e_cadherin_vimentin_expression_ratio,
            intermediate_hybrid_state_fraction=intermediate_hybrid_state_fraction,
            snail1_nuclear_translocation_tau_hours=snail1_nuclear_translocation_tau_hours,
            mesenchymal_migration_velocity_um_per_hr=mesenchymal_migration_velocity_um_per_hr,
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
    ) -> EmtSnailTwistContinuumItemProfile:
        item = EmtSnailTwistContinuumItemProfile(
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
    ) -> EmtSnailTwistContinuumMetricTrace:
        trace = EmtSnailTwistContinuumMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[EmtSnailTwistContinuumStudy]:
        result = await self.session.execute(
            select(EmtSnailTwistContinuumStudy)
            .options(
                selectinload(EmtSnailTwistContinuumStudy.item_profiles),
                selectinload(EmtSnailTwistContinuumStudy.metric_traces),
            )
            .where(EmtSnailTwistContinuumStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[EmtSnailTwistContinuumStudy]:
        result = await self.session.execute(
            select(EmtSnailTwistContinuumStudy)
            .options(
                selectinload(EmtSnailTwistContinuumStudy.item_profiles),
                selectinload(EmtSnailTwistContinuumStudy.metric_traces),
            )
            .order_by(EmtSnailTwistContinuumStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
