"""Repository for Phase 513: Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_quorum_sensing_cross_species_switch import (
    SyntheticQuorumSensingCrossSpeciesSwitchStudy,
    SyntheticQuorumSensingCrossSpeciesSwitchItemProfile,
    SyntheticQuorumSensingCrossSpeciesSwitchMetricTrace,
)


class SyntheticQuorumSensingCrossSpeciesSwitchRepository:
    """Database operations for Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Co-Cultured Synthetic E. coli and B. subtilis Biofilm with AI-2 / CAI-1 Inter-Species Relays",
        analytical_modality: str = "cross-species-quorum-switch",
        interbacterial_signal_induction_threshold_nM: float = 85.0,
        population_ratio_homeostasis_cv: float = 0.042,
        cross_repression_bistable_switch_delay_min: float = 18.5,
        metabolic_cross_feeding_syntrophy_rate_mM_per_hr: float = 3.2,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticQuorumSensingCrossSpeciesSwitchStudy:
        study = SyntheticQuorumSensingCrossSpeciesSwitchStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            interbacterial_signal_induction_threshold_nM=interbacterial_signal_induction_threshold_nM,
            population_ratio_homeostasis_cv=population_ratio_homeostasis_cv,
            cross_repression_bistable_switch_delay_min=cross_repression_bistable_switch_delay_min,
            metabolic_cross_feeding_syntrophy_rate_mM_per_hr=metabolic_cross_feeding_syntrophy_rate_mM_per_hr,
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
    ) -> SyntheticQuorumSensingCrossSpeciesSwitchItemProfile:
        item = SyntheticQuorumSensingCrossSpeciesSwitchItemProfile(
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
    ) -> SyntheticQuorumSensingCrossSpeciesSwitchMetricTrace:
        trace = SyntheticQuorumSensingCrossSpeciesSwitchMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticQuorumSensingCrossSpeciesSwitchStudy]:
        result = await self.session.execute(
            select(SyntheticQuorumSensingCrossSpeciesSwitchStudy)
            .options(
                selectinload(SyntheticQuorumSensingCrossSpeciesSwitchStudy.item_profiles),
                selectinload(SyntheticQuorumSensingCrossSpeciesSwitchStudy.metric_traces),
            )
            .where(SyntheticQuorumSensingCrossSpeciesSwitchStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SyntheticQuorumSensingCrossSpeciesSwitchStudy]:
        result = await self.session.execute(
            select(SyntheticQuorumSensingCrossSpeciesSwitchStudy)
            .options(
                selectinload(SyntheticQuorumSensingCrossSpeciesSwitchStudy.item_profiles),
                selectinload(SyntheticQuorumSensingCrossSpeciesSwitchStudy.metric_traces),
            )
            .order_by(SyntheticQuorumSensingCrossSpeciesSwitchStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
