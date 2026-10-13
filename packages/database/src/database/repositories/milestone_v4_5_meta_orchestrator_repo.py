"""Repository for Phase 455: Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_5_meta_orchestrator import (
    MilestoneV45MetaOrchestratorStudy,
    MilestoneV45MetaOrchestratorItemProfile,
    MilestoneV45MetaOrchestratorMetricTrace,
)


class MilestoneV45MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Unified Cross-Domain Multimodal Biosphere Supercomputing Matrix across 21 Research Studios",
        analytical_modality: str = "milestone-v4-5-planetary-synthesis",
        cross_modality_synthesis_entropy: float = 0.125,
        quantum_biomolecular_convergence_index: float = 0.994,
        consortium_supercomputing_orchestration_score: float = 0.988,
        grand_unification_fidelity_tau: float = 0.992,
        confidence_score: float = 0.999,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV45MetaOrchestratorStudy:
        study = MilestoneV45MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cross_modality_synthesis_entropy=cross_modality_synthesis_entropy,
            quantum_biomolecular_convergence_index=quantum_biomolecular_convergence_index,
            consortium_supercomputing_orchestration_score=consortium_supercomputing_orchestration_score,
            grand_unification_fidelity_tau=grand_unification_fidelity_tau,
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
    ) -> MilestoneV45MetaOrchestratorItemProfile:
        item = MilestoneV45MetaOrchestratorItemProfile(
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
    ) -> MilestoneV45MetaOrchestratorMetricTrace:
        trace = MilestoneV45MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV45MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV45MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV45MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV45MetaOrchestratorStudy.metric_traces),
            )
            .where(MilestoneV45MetaOrchestratorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MilestoneV45MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV45MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV45MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV45MetaOrchestratorStudy.metric_traces),
            )
            .order_by(MilestoneV45MetaOrchestratorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
