"""Milestone v1.6 Repo (Phase 125)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.milestone_v1_6 import DBMilestoneCentennialOrchestration

class MilestoneV16Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_orchestration_record(self, workspace_id: uuid.UUID, milestone_name: str,
                                          total_integrated_phases: int = 125,
                                          system_readiness_score: float = 99.8,
                                          active_domain_engines_count: int = 125) -> DBMilestoneCentennialOrchestration:
        m = DBMilestoneCentennialOrchestration(
            workspace_id=workspace_id,
            milestone_name=milestone_name,
            total_integrated_phases=total_integrated_phases,
            system_readiness_score=system_readiness_score,
            active_domain_engines_count=active_domain_engines_count,
        )
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def get_orchestration(self, record_id: uuid.UUID) -> Optional[DBMilestoneCentennialOrchestration]:
        res = await self.db.execute(select(DBMilestoneCentennialOrchestration).where(DBMilestoneCentennialOrchestration.id == record_id))
        return res.scalar_one_or_none()
