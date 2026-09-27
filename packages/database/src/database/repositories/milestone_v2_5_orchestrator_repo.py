"""Repository for Phase 231: Autonomous Milestone v2.5 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v2_5_orchestrator import (
    MilestoneV25OrchestratorStudy,
    MilestoneV25OrchestratorItemProfile,
    MilestoneV25OrchestratorMetricTrace,
)


class MilestoneV25OrchestratorRepository:
    """Database operations for Autonomous Milestone v2.5 Planetary Multi-Omics Research Synthesis & Meta-Orchestrator Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "milestone-v2-5-orchestrator",
        system_orchestration_synergy_index: float = 99.9,
        autonomous_workflow_throughput_qps: float = 1980.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV25OrchestratorStudy:
        study = MilestoneV25OrchestratorStudy(
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
    ) -> MilestoneV25OrchestratorItemProfile:
        item = MilestoneV25OrchestratorItemProfile(
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
    ) -> MilestoneV25OrchestratorMetricTrace:
        item = MilestoneV25OrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV25OrchestratorStudy]:
        stmt = select(MilestoneV25OrchestratorStudy).where(MilestoneV25OrchestratorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV25OrchestratorStudy]:
        stmt = select(MilestoneV25OrchestratorStudy).order_by(MilestoneV25OrchestratorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
