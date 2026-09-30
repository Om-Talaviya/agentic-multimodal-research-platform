"""Repository for Phase 392: Autonomous Milestone v4.2 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_2_meta_orchestrator import (
    MilestoneV42MetaOrchestratorStudy,
    MilestoneV42MetaOrchestratorItemProfile,
    MilestoneV42MetaOrchestratorMetricTrace,
)


class MilestoneV42MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v4.2 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "milestone-v4-2-orchestrator",
        meta_orchestrator_cross_domain_synthesis_coherence_pct: float = 99.99,
        planetary_scientific_workflow_dispatch_throughput_qps: float = 60000.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV42MetaOrchestratorStudy:
        study = MilestoneV42MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            meta_orchestrator_cross_domain_synthesis_coherence_pct=meta_orchestrator_cross_domain_synthesis_coherence_pct,
            planetary_scientific_workflow_dispatch_throughput_qps=planetary_scientific_workflow_dispatch_throughput_qps,
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
    ) -> MilestoneV42MetaOrchestratorItemProfile:
        item = MilestoneV42MetaOrchestratorItemProfile(
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
    ) -> MilestoneV42MetaOrchestratorMetricTrace:
        item = MilestoneV42MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV42MetaOrchestratorStudy]:
        stmt = select(MilestoneV42MetaOrchestratorStudy).where(MilestoneV42MetaOrchestratorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV42MetaOrchestratorStudy]:
        stmt = select(MilestoneV42MetaOrchestratorStudy).order_by(MilestoneV42MetaOrchestratorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
