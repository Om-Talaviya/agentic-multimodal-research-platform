"""Repository for Phase 518: Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v4_8_meta_orchestrator import (
    MilestoneV48MetaOrchestratorStudy,
    MilestoneV48MetaOrchestratorItemProfile,
    MilestoneV48MetaOrchestratorMetricTrace,
)


class MilestoneV48MetaOrchestratorRepository:
    """Database operations for Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Integrated Milestone v4.8 Synthetic Biofoundry, MRFM Quantum Imaging, CAST Transposase & Living Bioelectronics Suite",
        analytical_modality: str = "planetary-v4-8-meta-orchestration",
        synthetic_biofoundry_orchestration_coherence: float = 0.997,
        xenobiotic_chassis_cellular_compatibility_tau: float = 0.993,
        cross_engine_federated_convergence_ratio: float = 0.996,
        global_synthesis_confidence_score: float = 0.999,
        confidence_score: float = 0.999,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MilestoneV48MetaOrchestratorStudy:
        study = MilestoneV48MetaOrchestratorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            synthetic_biofoundry_orchestration_coherence=synthetic_biofoundry_orchestration_coherence,
            xenobiotic_chassis_cellular_compatibility_tau=xenobiotic_chassis_cellular_compatibility_tau,
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
    ) -> MilestoneV48MetaOrchestratorItemProfile:
        item = MilestoneV48MetaOrchestratorItemProfile(
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
    ) -> MilestoneV48MetaOrchestratorMetricTrace:
        trace = MilestoneV48MetaOrchestratorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV48MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV48MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV48MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV48MetaOrchestratorStudy.metric_traces),
            )
            .where(MilestoneV48MetaOrchestratorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MilestoneV48MetaOrchestratorStudy]:
        result = await self.session.execute(
            select(MilestoneV48MetaOrchestratorStudy)
            .options(
                selectinload(MilestoneV48MetaOrchestratorStudy.item_profiles),
                selectinload(MilestoneV48MetaOrchestratorStudy.metric_traces),
            )
            .order_by(MilestoneV48MetaOrchestratorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
