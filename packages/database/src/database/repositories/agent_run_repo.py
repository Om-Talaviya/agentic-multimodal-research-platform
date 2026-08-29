"""Agent run repository."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import AgentRun, ModelCall


class AgentRunRepository:
    """Repository for agent run operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, run: AgentRun) -> AgentRun:
        self.session.add(run)
        await self.session.flush()
        return run
    
    async def get(self, run_id: UUID) -> Optional[AgentRun]:
        result = await self.session.execute(
            select(AgentRun).where(AgentRun.id == run_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_job(self, job_id: UUID) -> List[AgentRun]:
        result = await self.session.execute(
            select(AgentRun)
            .where(AgentRun.job_id == job_id)
            .order_by(AgentRun.started_at)
        )
        return list(result.scalars().all())
    
    async def get_by_task(self, task_id: UUID) -> List[AgentRun]:
        result = await self.session.execute(
            select(AgentRun)
            .where(AgentRun.task_id == task_id)
            .order_by(AgentRun.started_at)
        )
        return list(result.scalars().all())
    
    async def complete(
        self, 
        run_id: UUID, 
        success: bool, 
        output: dict | None = None,
        errors: list[str] | None = None,
        duration_ms: int | None = None
    ) -> None:
        values = {
            "success": success,
            "completed_at": datetime.utcnow(),
        }
        if output:
            values["output"] = output
        if errors:
            values["errors"] = errors
        if duration_ms is not None:
            values["duration_ms"] = duration_ms
        
        await self.session.execute(
            update(AgentRun).where(AgentRun.id == run_id).values(**values)
        )
        await self.session.flush()


class ModelCallRepository:
    """Repository for model call operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, call: ModelCall) -> ModelCall:
        self.session.add(call)
        await self.session.flush()
        return call
    
    async def create_batch(self, calls: List[ModelCall]) -> List[ModelCall]:
        self.session.add_all(calls)
        await self.session.flush()
        return calls
    
    async def get_by_agent_run(self, agent_run_id: UUID) -> List[ModelCall]:
        result = await self.session.execute(
            select(ModelCall)
            .where(ModelCall.agent_run_id == agent_run_id)
            .order_by(ModelCall.created_at)
        )
        return list(result.scalars().all())