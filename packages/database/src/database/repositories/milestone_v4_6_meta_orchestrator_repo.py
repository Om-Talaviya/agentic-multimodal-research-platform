"""Repository for Phase 476: Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_6_meta_orchestrator import (
    MilestoneV46MetaOrchestratorStudy,
    MilestoneV46MetaOrchestratorItemProfile,
    MilestoneV46MetaOrchestratorMetricTrace,
)


class MilestoneV46MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Integrated Milestone v4.6 Multi-Tissue Synthetic Morphogenesis, Biohybrid Soft Cybernetics & Multicellular Engine Suite",
        analytical_modality: str = "planetary-v4-6-meta-orchestration",
        multicellular_morphogenesis_coherence_index: float = 0.995,
        biohybrid_actuation_cybernetic_sync_tau: float = 0.988,
        cross_engine_federated_convergence_ratio: float = 0.992,
        global_synthesis_confidence_score: float = 0.997,
        confidence_score: float = 0.998,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV46MetaOrchestratorStudy:
        study = MilestoneV46MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            multicellular_morphogenesis_coherence_index=multicellular_morphogenesis_coherence_index,
            biohybrid_actuation_cybernetic_sync_tau=biohybrid_actuation_cybernetic_sync_tau,
            cross_engine_federated_convergence_ratio=cross_engine_federated_convergence_ratio,
            global_synthesis_confidence_score=global_synthesis_confidence_score,
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
    ) -> MilestoneV46MetaOrchestratorItemProfile:
        item = MilestoneV46MetaOrchestratorItemProfile(
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
    ) -> MilestoneV46MetaOrchestratorMetricTrace:
        trace = MilestoneV46MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV46MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV46MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV46MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV46MetaOrchestratorStudy.metric_traces),
            )
            .where(MilestoneV46MetaOrchestratorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MilestoneV46MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV46MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV46MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV46MetaOrchestratorStudy.metric_traces),
            )
            .order_by(MilestoneV46MetaOrchestratorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
