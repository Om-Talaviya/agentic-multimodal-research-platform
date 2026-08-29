"""Research job repository."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from database.models import ResearchJob, ResearchTask, Source, Evidence
from shared.types import TaskStatus, JobStatus


class ResearchJobRepository:
    """Repository for research job operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, job: ResearchJob) -> ResearchJob:
        self.session.add(job)
        await self.session.flush()
        return job
    
    async def get(self, job_id: UUID) -> Optional[ResearchJob]:
        result = await self.session.execute(
            select(ResearchJob).where(ResearchJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_relations(self, job_id: UUID) -> Optional[ResearchJob]:
        result = await self.session.execute(
            select(ResearchJob)
            .options(
                selectinload(ResearchJob.tasks),
                selectinload(ResearchJob.sources),
                selectinload(ResearchJob.evidence),
                selectinload(ResearchJob.documents),
                selectinload(ResearchJob.reports),
            )
            .where(ResearchJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(
        self, 
        job_id: UUID, 
        status: JobStatus, 
        error: str | None = None
    ) -> None:
        values = {"status": status.value, "updated_at": datetime.utcnow()}
        if error:
            values["error_message"] = error
        if status == JobStatus.COMPLETED:
            values["completed_at"] = datetime.utcnow()
        elif status == JobStatus.FAILED:
            values["completed_at"] = datetime.utcnow()
        
        await self.session.execute(
            update(ResearchJob).where(ResearchJob.id == job_id).values(**values)
        )
        await self.session.flush()
    
    async def list_jobs(
        self, 
        limit: int = 50, 
        offset: int = 0,
        status: JobStatus | None = None
    ) -> List[ResearchJob]:
        query = select(ResearchJob).order_by(ResearchJob.created_at.desc())
        if status:
            query = query.where(ResearchJob.status == status.value)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_jobs(self, status: JobStatus | None = None) -> int:
        query = select(func.count(ResearchJob.id))
        if status:
            query = query.where(ResearchJob.status == status.value)
        result = await self.session.execute(query)
        return result.scalar_one()


class TaskRepository:
    """Repository for task operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, task: ResearchTask) -> ResearchTask:
        self.session.add(task)
        await self.session.flush()
        return task
    
    async def create_batch(self, tasks: List[ResearchTask]) -> List[ResearchTask]:
        self.session.add_all(tasks)
        await self.session.flush()
        return tasks
    
    async def get(self, task_id: UUID) -> Optional[ResearchTask]:
        result = await self.session.execute(
            select(ResearchTask).where(ResearchTask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_job(self, job_id: UUID) -> List[ResearchTask]:
        result = await self.session.execute(
            select(ResearchTask)
            .where(ResearchTask.job_id == job_id)
            .order_by(ResearchTask.priority, ResearchTask.created_at)
        )
        return list(result.scalars().all())
    
    async def update_status(
        self, 
        task_id: UUID, 
        status: TaskStatus, 
        error: str | None = None,
        result: dict | None = None
    ) -> None:
        values = {"status": status.value}
        if status == TaskStatus.RUNNING:
            values["started_at"] = datetime.utcnow()
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            values["completed_at"] = datetime.utcnow()
        if error:
            values["error_message"] = error
        if result:
            values["result"] = result
        
        await self.session.execute(
            update(ResearchTask).where(ResearchTask.id == task_id).values(**values)
        )
        await self.session.flush()


class SourceRepository:
    """Repository for source operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, source: Source) -> Source:
        self.session.add(source)
        await self.session.flush()
        return source
    
    async def create_batch(self, sources: List[Source]) -> List[Source]:
        self.session.add_all(sources)
        await self.session.flush()
        return sources
    
    async def get(self, source_id: UUID) -> Optional[Source]:
        result = await self.session.execute(
            select(Source).where(Source.id == source_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_job(self, job_id: UUID) -> List[Source]:
        result = await self.session.execute(
            select(Source).where(Source.job_id == job_id)
        )
        return list(result.scalars().all())
    
    async def get_by_content_hash(self, content_hash: str) -> Optional[Source]:
        result = await self.session.execute(
            select(Source).where(Source.content_hash == content_hash)
        )
        return result.scalar_one_or_none()


class EvidenceRepository:
    """Repository for evidence operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, evidence: Evidence) -> Evidence:
        self.session.add(evidence)
        await self.session.flush()
        return evidence
    
    async def create_batch(self, evidence_list: List[Evidence]) -> List[Evidence]:
        self.session.add_all(evidence_list)
        await self.session.flush()
        return evidence_list
    
    async def get_by_job(self, job_id: UUID) -> List[Evidence]:
        result = await self.session.execute(
            select(Evidence).where(Evidence.job_id == job_id)
        )
        return list(result.scalars().all())
    
    async def get_by_source(self, source_id: UUID) -> List[Evidence]:
        result = await self.session.execute(
            select(Evidence).where(Evidence.source_id == source_id)
        )
        return list(result.scalars().all())
    
    async def update_verification(
        self, 
        evidence_id: UUID, 
        status: str, 
        confidence: float | None = None,
        notes: str | None = None
    ) -> None:
        values = {"verification_status": status}
        if confidence is not None:
            values["confidence"] = confidence
        if notes is not None:
            values["verification_notes"] = notes
        
        await self.session.execute(
            update(Evidence).where(Evidence.id == evidence_id).values(**values)
        )
        await self.session.flush()