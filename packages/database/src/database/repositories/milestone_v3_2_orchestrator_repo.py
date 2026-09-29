"""Repository for Phase 280: Autonomous Milestone v3.2 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v3_2_orchestrator import (
    MilestoneV32OrchestratorStudy,
    MilestoneV32OrchestratorItemProfile,
    MilestoneV32OrchestratorMetricTrace,
)


class MilestoneV32OrchestratorRepository:
    """Database operations for Autonomous Milestone v3.2 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "milestone-v3-2-orchestrator",
        cross_modal_orchestration_consensus_index: float = 99.8,
        autonomous_pipeline_completion_rate_pct: float = 100.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV32OrchestratorStudy:
        study = MilestoneV32OrchestratorStudy(
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
    ) -> MilestoneV32OrchestratorItemProfile:
        item = MilestoneV32OrchestratorItemProfile(
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
    ) -> MilestoneV32OrchestratorMetricTrace:
        item = MilestoneV32OrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV32OrchestratorStudy]:
        stmt = select(MilestoneV32OrchestratorStudy).where(MilestoneV32OrchestratorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV32OrchestratorStudy]:
        stmt = select(MilestoneV32OrchestratorStudy).order_by(MilestoneV32OrchestratorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
