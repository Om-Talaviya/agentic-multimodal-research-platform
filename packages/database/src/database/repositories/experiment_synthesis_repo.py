"""Repository for Autonomous Experiment Synthesis data access (Phase 100)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.experiment_synthesis import (
    DBAutonomousExperimentSynthesis,
    DBAutonomousActionStep,
    DBClosedLoopVerificationRecord,
)


class ExperimentSynthesisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_synthesis(
        self,
        workspace_id: uuid.UUID,
        campaign_title: str,
        scientific_domain: str,
        hypothesis_statement: str,
        synthesis_summary: str,
        autonomous_state: str = "COMPLETED",
        overall_confidence_score: float = 96.5,
        total_pipeline_stages: int = 5,
        completed_stages_count: int = 5,
        synthesis_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBAutonomousExperimentSynthesis:
        syn = DBAutonomousExperimentSynthesis(
            workspace_id=workspace_id,
            campaign_title=campaign_title,
            scientific_domain=scientific_domain,
            hypothesis_statement=hypothesis_statement,
            synthesis_summary=synthesis_summary,
            autonomous_state=autonomous_state,
            overall_confidence_score=overall_confidence_score,
            total_pipeline_stages=total_pipeline_stages,
            completed_stages_count=completed_stages_count,
            synthesis_metadata=synthesis_metadata or {},
        )
        self.session.add(syn)
        await self.session.commit()
        await self.session.refresh(syn)
        return syn

    async def add_action_step(
        self,
        synthesis_id: uuid.UUID,
        step_number: int,
        stage_name: str,
        agent_persona: str,
        output_summary: str,
        execution_status: str = "SUCCESS",
        latency_seconds: float = 1.85,
    ) -> DBAutonomousActionStep:
        step = DBAutonomousActionStep(
            synthesis_id=synthesis_id,
            step_number=step_number,
            stage_name=stage_name,
            agent_persona=agent_persona,
            output_summary=output_summary,
            execution_status=execution_status,
            latency_seconds=latency_seconds,
        )
        self.session.add(step)
        await self.session.commit()
        await self.session.refresh(step)
        return step

    async def add_verification(
        self,
        synthesis_id: uuid.UUID,
        metric_name: str,
        expected_value: float,
        observed_value: float,
        deviation_pct: float = 1.2,
        verification_passed: str = "PASSED",
    ) -> DBClosedLoopVerificationRecord:
        ver = DBClosedLoopVerificationRecord(
            synthesis_id=synthesis_id,
            metric_name=metric_name,
            expected_value=expected_value,
            observed_value=observed_value,
            deviation_pct=deviation_pct,
            verification_passed=verification_passed,
        )
        self.session.add(ver)
        await self.session.commit()
        await self.session.refresh(ver)
        return ver

    async def get_synthesis(self, synthesis_id: uuid.UUID) -> Optional[DBAutonomousExperimentSynthesis]:
        stmt = (
            select(DBAutonomousExperimentSynthesis)
            .options(
                selectinload(DBAutonomousExperimentSynthesis.action_steps),
                selectinload(DBAutonomousExperimentSynthesis.verifications),
            )
            .where(DBAutonomousExperimentSynthesis.id == synthesis_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
