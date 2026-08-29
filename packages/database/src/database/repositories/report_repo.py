"""Report repository."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Report


class ReportRepository:
    """Repository for report operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.flush()
        return report
    
    async def get(self, report_id: UUID) -> Optional[Report]:
        result = await self.session.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_job(self, job_id: UUID) -> Optional[Report]:
        result = await self.session.execute(
            select(Report).where(Report.job_id == job_id)
        )
        return result.scalar_one_or_none()