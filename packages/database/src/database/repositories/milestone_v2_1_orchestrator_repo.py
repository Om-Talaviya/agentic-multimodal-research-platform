"""Repository for Phase 187: Milestone v2.1 Planetary Meta-Orchestrator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.milestone_v2_1_orchestrator import (
    MilestoneV21SynthesisStudy,
    MilestoneV21SubsystemTelemetry,
    MilestoneV21PlanetaryRun,
)


class MilestoneV21OrchestratorRepository:
    """Database operations for Milestone v2.1 planetary orchestration studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        mission_scope: str = "Planetary Multimodal Autonomous Synthesis",
        active_subsystems_count: int = 187,
        global_cross_correlation_index: float = 0.982,
        synthesis_confidence_score: float = 0.994,
        autonomous_discovery_throughput: float = 420.0,
        status: str = "completed",
        orchestration_parameters: dict = None,
        executive_synthesis_report: str = "",
    ) -> MilestoneV21SynthesisStudy:
        study = MilestoneV21SynthesisStudy(
            name=name,
            mission_scope=mission_scope,
            active_subsystems_count=active_subsystems_count,
            global_cross_correlation_index=global_cross_correlation_index,
            synthesis_confidence_score=synthesis_confidence_score,
            autonomous_discovery_throughput=autonomous_discovery_throughput,
            status=status,
            orchestration_parameters=orchestration_parameters or {},
            executive_synthesis_report=executive_synthesis_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_telemetry(
        self,
        study_id: UUID,
        subsystem_domain: str,
        subsystem_phase_code: str,
        throughput_ops_sec: float,
        cross_validation_accuracy: float,
        latency_ms: float,
    ) -> MilestoneV21SubsystemTelemetry:
        item = MilestoneV21SubsystemTelemetry(
            study_id=study_id,
            subsystem_domain=subsystem_domain,
            subsystem_phase_code=subsystem_phase_code,
            throughput_ops_sec=throughput_ops_sec,
            cross_validation_accuracy=cross_validation_accuracy,
            latency_ms=latency_ms,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_planetary_run(
        self,
        study_id: UUID,
        run_identifier: str,
        generated_hypotheses: int,
        validated_lead_targets: int,
        meta_synthesis_entropy: float,
    ) -> MilestoneV21PlanetaryRun:
        item = MilestoneV21PlanetaryRun(
            study_id=study_id,
            run_identifier=run_identifier,
            generated_hypotheses=generated_hypotheses,
            validated_lead_targets=validated_lead_targets,
            meta_synthesis_entropy=meta_synthesis_entropy,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[MilestoneV21SynthesisStudy]:
        stmt = select(MilestoneV21SynthesisStudy).where(MilestoneV21SynthesisStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MilestoneV21SynthesisStudy]:
        stmt = select(MilestoneV21SynthesisStudy).order_by(MilestoneV21SynthesisStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
