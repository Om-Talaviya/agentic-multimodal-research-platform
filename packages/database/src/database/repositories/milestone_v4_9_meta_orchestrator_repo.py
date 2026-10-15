"""Repository for Phase 539: Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_9_meta_orchestrator import (
    MilestoneV49MetaOrchestratorStudy,
    MilestoneV49MetaOrchestratorItemProfile,
    MilestoneV49MetaOrchestratorMetricTrace,
)


class MilestoneV49MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Global Milestone v4.9 Distributed Multi-Agent DAG Across Phases 519-539",
        analytical_modality: str = "milestone-v4-9-planetary-orchestration",
        cross_phase_dag_convergence_tau: float = 0.998,
        multi_agent_consensus_fidelity_pct: float = 99.5,
        sub_angstrom_simulation_accuracy_score: float = 0.994,
        closed_loop_autonomous_cycle_time_s: float = 14.2,
        confidence_score: float = 0.999,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV49MetaOrchestratorStudy:
        study = MilestoneV49MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cross_phase_dag_convergence_tau=cross_phase_dag_convergence_tau,
            multi_agent_consensus_fidelity_pct=multi_agent_consensus_fidelity_pct,
            sub_angstrom_simulation_accuracy_score=sub_angstrom_simulation_accuracy_score,
            closed_loop_autonomous_cycle_time_s=closed_loop_autonomous_cycle_time_s,
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
    ) -> MilestoneV49MetaOrchestratorItemProfile:
        item = MilestoneV49MetaOrchestratorItemProfile(
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
    ) -> MilestoneV49MetaOrchestratorMetricTrace:
        trace = MilestoneV49MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV49MetaOrchestratorStudy]:
        stmt = (
            select(MilestoneV49MetaOrchestratorStudy)
            .where(MilestoneV49MetaOrchestratorStudy.id == study_id)
            .options(
                selectinload(MilestoneV49MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV49MetaOrchestratorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MilestoneV49MetaOrchestratorStudy]:
        stmt = (
            select(MilestoneV49MetaOrchestratorStudy)
            .order_by(MilestoneV49MetaOrchestratorStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MilestoneV49MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV49MetaOrchestratorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
