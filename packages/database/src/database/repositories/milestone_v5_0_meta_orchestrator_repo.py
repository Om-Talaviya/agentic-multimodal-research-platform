"""Repository for Phase 560: Autonomous Milestone v5.0 Planetary Multi-Scale Biodynamics, Quantum Bio-Spintronics & Cellular Reprogramming OS Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v5_0_meta_orchestrator import (
    MilestoneV50MetaOrchestratorStudy,
    MilestoneV50MetaOrchestratorItemProfile,
    MilestoneV50MetaOrchestratorMetricTrace,
)


class MilestoneV50MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v5.0 Planetary Multi-Scale Biodynamics, Quantum Bio-Spintronics & Cellular Reprogramming OS Grand Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Full Planetary Biodynamics, Quantum Spin Sensing, Direct RNA, Neuromorphic Optogenetics & Cellular Reprogramming Unified Grid",
        analytical_modality: str = "planetary-v5-0-meta-orchestration",
        multi_scale_cross_engine_coupling_efficiency_pct: float = 99.8,
        quantum_spintronic_fidelity_index: float = 0.994,
        subcellular_reprogramming_convergence_rate: float = 0.985,
        total_orchestrated_milestone_phases: float = 560.0,
        confidence_score: float = 0.999,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV50MetaOrchestratorStudy:
        study = MilestoneV50MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            multi_scale_cross_engine_coupling_efficiency_pct=multi_scale_cross_engine_coupling_efficiency_pct,
            quantum_spintronic_fidelity_index=quantum_spintronic_fidelity_index,
            subcellular_reprogramming_convergence_rate=subcellular_reprogramming_convergence_rate,
            total_orchestrated_milestone_phases=total_orchestrated_milestone_phases,
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
    ) -> MilestoneV50MetaOrchestratorItemProfile:
        item = MilestoneV50MetaOrchestratorItemProfile(
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
    ) -> MilestoneV50MetaOrchestratorMetricTrace:
        trace = MilestoneV50MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV50MetaOrchestratorStudy]:
        stmt = (
            select(MilestoneV50MetaOrchestratorStudy)
            .where(MilestoneV50MetaOrchestratorStudy.id == study_id)
            .options(
                selectinload(MilestoneV50MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV50MetaOrchestratorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MilestoneV50MetaOrchestratorStudy]:
        stmt = (
            select(MilestoneV50MetaOrchestratorStudy)
            .order_by(MilestoneV50MetaOrchestratorStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MilestoneV50MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV50MetaOrchestratorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
