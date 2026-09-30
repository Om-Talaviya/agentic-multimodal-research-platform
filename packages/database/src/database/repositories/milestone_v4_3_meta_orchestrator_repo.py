"""Repository for Phase 413: Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_3_meta_orchestrator import (
    MilestoneV43MetaOrchestratorStudy,
    MilestoneV43MetaOrchestratorItemProfile,
    MilestoneV43MetaOrchestratorMetricTrace,
)


class MilestoneV43MetaOrchestratorRepository:
    """Database operations for Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "milestone-v4-3-meta-orchestration",
        global_system_synthesis_coherence_index: float = 0.999,
        cross_modal_autonomous_research_throughput_fold: float = 185.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV43MetaOrchestratorStudy:
        study = MilestoneV43MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            global_system_synthesis_coherence_index=global_system_synthesis_coherence_index,
            cross_modal_autonomous_research_throughput_fold=cross_modal_autonomous_research_throughput_fold,
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
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> MilestoneV43MetaOrchestratorItemProfile:
        item = MilestoneV43MetaOrchestratorItemProfile(
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
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> MilestoneV43MetaOrchestratorMetricTrace:
        item = MilestoneV43MetaOrchestratorMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV43MetaOrchestratorStudy]:
        stmt = select(MilestoneV43MetaOrchestratorStudy).where(MilestoneV43MetaOrchestratorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV43MetaOrchestratorStudy]:
        stmt = select(MilestoneV43MetaOrchestratorStudy).order_by(MilestoneV43MetaOrchestratorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
