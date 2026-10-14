"""Repository for Phase 492: Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.human_on_chip_endocrine_feedback import (
    HumanOnChipEndocrineFeedbackStudy,
    HumanOnChipEndocrineFeedbackItemProfile,
    HumanOnChipEndocrineFeedbackMetricTrace,
)


class HumanOnChipEndocrineFeedbackRepository:
    """Database operations for Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "4-Organ Interconnected Microfluidic Platform (Liver Spheroids, Islet Organoids, Adipose, Skeletal Muscle)",
        analytical_modality: str = "human-on-chip-endocrine-loop",
        glucose_stimulated_insulin_secretion_gsis_index: float = 3.85,
        hepatic_glucose_uptake_rate_uM_per_hr: float = 42.0,
        inter_organ_circulatory_perfusion_flow_uL_per_min: float = 5.0,
        homeostatic_endocrine_feedback_sync_tau: float = 0.985,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> HumanOnChipEndocrineFeedbackStudy:
        study = HumanOnChipEndocrineFeedbackStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            glucose_stimulated_insulin_secretion_gsis_index=glucose_stimulated_insulin_secretion_gsis_index,
            hepatic_glucose_uptake_rate_uM_per_hr=hepatic_glucose_uptake_rate_uM_per_hr,
            inter_organ_circulatory_perfusion_flow_uL_per_min=inter_organ_circulatory_perfusion_flow_uL_per_min,
            homeostatic_endocrine_feedback_sync_tau=homeostatic_endocrine_feedback_sync_tau,
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
    ) -> HumanOnChipEndocrineFeedbackItemProfile:
        item = HumanOnChipEndocrineFeedbackItemProfile(
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
    ) -> HumanOnChipEndocrineFeedbackMetricTrace:
        trace = HumanOnChipEndocrineFeedbackMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[HumanOnChipEndocrineFeedbackStudy]:
        result = await self.session.execute(
            select(HumanOnChipEndocrineFeedbackStudy)
            .options(
                selectinload(HumanOnChipEndocrineFeedbackStudy.item_profiles),
                selectinload(HumanOnChipEndocrineFeedbackStudy.metric_traces),
            )
            .where(HumanOnChipEndocrineFeedbackStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[HumanOnChipEndocrineFeedbackStudy]:
        result = await self.session.execute(
            select(HumanOnChipEndocrineFeedbackStudy)
            .options(
                selectinload(HumanOnChipEndocrineFeedbackStudy.item_profiles),
                selectinload(HumanOnChipEndocrineFeedbackStudy.metric_traces),
            )
            .order_by(HumanOnChipEndocrineFeedbackStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
