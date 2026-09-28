"""Repository for Phase 252: Autonomous Milestone v2.8 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v2_8_orchestrator import (
    MilestoneV28OrchestratorStudy,
    MilestoneV28OrchestratorItemProfile,
    MilestoneV28OrchestratorMetricTrace,
)


class MilestoneV28OrchestratorRepository:
    """Database operations for Autonomous Milestone v2.8 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "milestone-v2-8-orchestrator",
        cross_modal_orchestration_consensus_index: float = 99.6,
        autonomous_pipeline_completion_rate_pct: float = 100.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV28OrchestratorStudy:
        study = MilestoneV28OrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cross_modal_orchestration_consensus_index=cross_modal_orchestration_consensus_index,
            autonomous_pipeline_completion_rate_pct=autonomous_pipeline_completion_rate_pct,
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
    ) -> MilestoneV28OrchestratorItemProfile:
        item = MilestoneV28OrchestratorItemProfile(
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
    ) -> MilestoneV28OrchestratorMetricTrace:
        item = MilestoneV28OrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV28OrchestratorStudy]:
        stmt = select(MilestoneV28OrchestratorStudy).where(MilestoneV28OrchestratorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV28OrchestratorStudy]:
        stmt = select(MilestoneV28OrchestratorStudy).order_by(MilestoneV28OrchestratorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
