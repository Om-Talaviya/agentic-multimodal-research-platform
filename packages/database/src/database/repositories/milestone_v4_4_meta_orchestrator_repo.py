"""Repository for Phase 434: Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_4_meta_orchestrator import (
    MilestoneV44MetaOrchestratorStudy,
    MilestoneV44MetaOrchestratorItemProfile,
    MilestoneV44MetaOrchestratorMetricTrace,
)


class MilestoneV44MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Planetary Multi-Scale Biophysical & Epitranscriptomic Synthesis Consortium",
        analytical_modality: str = "milestone-v4-4-meta-orchestrator",
        cross_phase_coherence_index: float = 0.998,
        dag_pipeline_throughput_jobs_per_s: float = 185.0,
        multi_modal_synthesis_confidence: float = 0.999,
        autonomous_discovery_convergence_tau: float = 0.985,
        confidence_score: float = 0.999,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV44MetaOrchestratorStudy:
        study = MilestoneV44MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cross_phase_coherence_index=cross_phase_coherence_index,
            dag_pipeline_throughput_jobs_per_s=dag_pipeline_throughput_jobs_per_s,
            multi_modal_synthesis_confidence=multi_modal_synthesis_confidence,
            autonomous_discovery_convergence_tau=autonomous_discovery_convergence_tau,
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
    ) -> MilestoneV44MetaOrchestratorItemProfile:
        item = MilestoneV44MetaOrchestratorItemProfile(
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
    ) -> MilestoneV44MetaOrchestratorMetricTrace:
        trace = MilestoneV44MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV44MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV44MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV44MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV44MetaOrchestratorStudy.metric_traces),
            )
            .where(MilestoneV44MetaOrchestratorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MilestoneV44MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV44MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV44MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV44MetaOrchestratorStudy.metric_traces),
            )
            .order_by(MilestoneV44MetaOrchestratorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
