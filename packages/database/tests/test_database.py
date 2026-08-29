"""Tests for database package."""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import TypeDecorator, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from database.connection import Base, init_db
from database.models import ResearchJob, ResearchTask, Source, Evidence, Document, DocumentChunk, Report, AgentRun, ModelCall
from database.repositories import ResearchJobRepository, TaskRepository, SourceRepository, EvidenceRepository
from shared.types import TaskStatus, JobStatus


class JSONBType(TypeDecorator):
    """JSONB type that falls back to JSON for SQLite."""
    
    impl = Text
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(JSON())


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def job_repo(test_session):
    return ResearchJobRepository(test_session)


@pytest_asyncio.fixture
async def task_repo(test_session):
    return TaskRepository(test_session)


@pytest_asyncio.fixture
async def source_repo(test_session):
    return SourceRepository(test_session)


@pytest_asyncio.fixture
async def evidence_repo(test_session):
    return EvidenceRepository(test_session)


async def test_create_and_get_job(job_repo):
    """Test creating and retrieving a research job."""
    job = ResearchJob(
        request_id=uuid4(),
        question="Test question",
        objective="Test objective",
        domain="test",
        status=JobStatus.PENDING,
    )
    
    created = await job_repo.create(job)
    assert created.id is not None
    assert created.question == "Test question"
    
    fetched = await job_repo.get(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.question == "Test question"


async def test_update_job_status(job_repo):
    """Test updating job status."""
    job = ResearchJob(
        request_id=uuid4(),
        question="Test",
        objective="Test",
        status=JobStatus.PENDING,
    )
    created = await job_repo.create(job)
    
    await job_repo.update_status(created.id, JobStatus.RUNNING)
    
    fetched = await job_repo.get(created.id)
    assert fetched.status == JobStatus.RUNNING.value
    assert fetched.started_at is not None
    
    await job_repo.update_status(created.id, JobStatus.COMPLETED)
    fetched = await job_repo.get(created.id)
    assert fetched.status == JobStatus.COMPLETED.value
    assert fetched.completed_at is not None


async def test_list_jobs(job_repo):
    """Test listing jobs."""
    for i in range(3):
        job = ResearchJob(
            request_id=uuid4(),
            question=f"Question {i}",
            objective=f"Objective {i}",
            status=JobStatus.PENDING,
        )
        await job_repo.create(job)
    
    jobs = await job_repo.list_jobs(limit=10)
    assert len(jobs) == 3
    
    # Test pagination
    jobs = await job_repo.list_jobs(limit=2, offset=1)
    assert len(jobs) == 2


async def test_create_and_get_task(task_repo):
    """Test creating and retrieving a task."""
    task = ResearchTask(
        job_id=uuid4(),
        type="web_research",
        objective="Search web",
        agent="web_research",
        status=TaskStatus.PENDING,
    )
    
    created = await task_repo.create(task)
    assert created.id is not None
    
    fetched = await task_repo.get(created.id)
    assert fetched is not None
    assert fetched.objective == "Search web"


async def test_update_task_status(task_repo):
    """Test updating task status."""
    task = ResearchTask(
        job_id=uuid4(),
        type="web_research",
        objective="Search web",
        agent="web_research",
        status=TaskStatus.PENDING,
    )
    created = await task_repo.create(task)
    
    await task_repo.update_status(created.id, TaskStatus.RUNNING)
    fetched = await task_repo.get(created.id)
    assert fetched.status == TaskStatus.RUNNING.value
    assert fetched.started_at is not None
    
    await task_repo.update_status(created.id, TaskStatus.COMPLETED, result={"sources": 5})
    fetched = await task_repo.get(created.id)
    assert fetched.status == TaskStatus.COMPLETED.value
    assert fetched.result == {"sources": 5}


async def test_create_source(source_repo):
    """Test creating a source."""
    source = Source(
        job_id=uuid4(),
        type="web",
        url="https://example.com",
        title="Example",
        source_metadata={"domain": "example.com"},
    )
    
    created = await source_repo.create(source)
    assert created.id is not None
    assert created.url == "https://example.com"


async def test_create_evidence(evidence_repo):
    """Test creating evidence."""
    source_id = uuid4()
    evidence = Evidence(
        job_id=uuid4(),
        source_id=source_id,
        claim="Test claim",
        supporting_text="Test evidence",
        confidence=0.8,
    )
    
    created = await evidence_repo.create(evidence)
    assert created.id is not None
    assert created.claim == "Test claim"
    assert created.confidence == 0.8


async def test_update_evidence_verification(evidence_repo):
    """Test updating evidence verification status."""
    evidence = Evidence(
        job_id=uuid4(),
        source_id=uuid4(),
        claim="Test",
        supporting_text="Test",
        confidence=0.5,
    )
    created = await evidence_repo.create(evidence)
    
    await evidence_repo.update_verification(created.id, "consensus", 0.9, "Verified by multiple sources")
    
    fetched = await evidence_repo.get_by_job(created.job_id)
    assert len(fetched) == 1
    assert fetched[0].verification_status == "consensus"
    assert fetched[0].confidence == 0.9
    assert fetched[0].verification_notes == "Verified by multiple sources"