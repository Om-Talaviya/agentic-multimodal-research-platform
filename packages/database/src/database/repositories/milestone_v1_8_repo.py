"""Repository for Milestone v1.8 Synthesis (Phase 154)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.milestone_v1_8 import (
    DBMilestoneV18Orchestration,
    DBCrossDomainWorkflowNode,
    DBSynthesisExecutiveReport,
)


class MilestoneV18Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_orchestration(
        self,
        orchestration_name: str,
        milestone_version: str,
        total_phases_integrated: int,
        cross_domain_pipeline_status: str,
        orchestration_confidence_score: float,
        global_system_entropy: float,
    ) -> DBMilestoneV18Orchestration:
        orch = DBMilestoneV18Orchestration(
            id=uuid.uuid4(),
            orchestration_name=orchestration_name,
            milestone_version=milestone_version,
            total_phases_integrated=total_phases_integrated,
            cross_domain_pipeline_status=cross_domain_pipeline_status,
            orchestration_confidence_score=orchestration_confidence_score,
            global_system_entropy=global_system_entropy,
        )
        self.db.add(orch)
        await self.db.commit()
        await self.db.refresh(orch)
        return orch

    async def add_workflow_node(
        self,
        orchestration_id: uuid.UUID,
        node_name: str,
        domain_category: str,
        phase_reference: str,
        execution_latency_ms: float,
        node_fidelity_score: float,
    ) -> DBCrossDomainWorkflowNode:
        rec = DBCrossDomainWorkflowNode(
            id=uuid.uuid4(),
            orchestration_id=orchestration_id,
            node_name=node_name,
            domain_category=domain_category,
            phase_reference=phase_reference,
            execution_latency_ms=execution_latency_ms,
            node_fidelity_score=node_fidelity_score,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_executive_report(
        self,
        orchestration_id: uuid.UUID,
        report_title: str,
        executive_summary: str,
        primary_breakthrough: str,
        recommended_clinical_translation: str,
    ) -> DBSynthesisExecutiveReport:
        rec = DBSynthesisExecutiveReport(
            id=uuid.uuid4(),
            orchestration_id=orchestration_id,
            report_title=report_title,
            executive_summary=executive_summary,
            primary_breakthrough=primary_breakthrough,
            recommended_clinical_translation=recommended_clinical_translation,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_orchestration_with_details(self, orchestration_id: uuid.UUID) -> Optional[DBMilestoneV18Orchestration]:
        stmt = (
            select(DBMilestoneV18Orchestration)
            .where(DBMilestoneV18Orchestration.id == orchestration_id)
            .options(
                selectinload(DBMilestoneV18Orchestration.workflow_nodes),
                selectinload(DBMilestoneV18Orchestration.synthesis_reports),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
