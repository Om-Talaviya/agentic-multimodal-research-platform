"""Repository for Phase 224: Autonomous Milestone v2.4 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v2_4_orchestrator import (
    MilestoneV24OrchestratorStudy,
    MilestoneV24OrchestratorItemProfile,
    MilestoneV24OrchestratorMetricTrace,
)


class MilestoneV24OrchestratorRepository:
    """Database operations for Autonomous Milestone v2.4 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "milestone-v2-4-orchestrator",
        system_orchestration_synergy_index: float = 99.8,
        autonomous_workflow_throughput_qps: float = 1850.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV24OrchestratorStudy:
        study = MilestoneV24OrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            system_orchestration_synergy_index=system_orchestration_synergy_index,
            autonomous_workflow_throughput_qps=autonomous_workflow_throughput_qps,
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
    ) -> MilestoneV24OrchestratorItemProfile:
        item = MilestoneV24OrchestratorItemProfile(
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
    ) -> MilestoneV24OrchestratorMetricTrace:
        item = MilestoneV24OrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV24OrchestratorStudy]:
        stmt = select(MilestoneV24OrchestratorStudy).where(MilestoneV24OrchestratorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV24OrchestratorStudy]:
        stmt = select(MilestoneV24OrchestratorStudy).order_by(MilestoneV24OrchestratorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
