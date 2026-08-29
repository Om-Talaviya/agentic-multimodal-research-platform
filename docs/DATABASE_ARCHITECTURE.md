# Database Architecture

## Overview

Three separate data stores for different access patterns:

1. **PostgreSQL** - Relational data (jobs, tasks, users, metadata)
2. **ChromaDB** - Vector embeddings for semantic search
3. **File Storage** - Raw uploads and processed assets

## PostgreSQL Schema

### Core Tables

```sql
-- Research jobs
CREATE TABLE research_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    question TEXT NOT NULL,
    objective TEXT NOT NULL,
    domain VARCHAR(255),
    scope TEXT,
    constraints JSONB DEFAULT '[]',
    expected_output VARCHAR(100) DEFAULT 'report',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX idx_research_jobs_status ON research_jobs(status);
CREATE INDEX idx_research_jobs_created_at ON research_jobs(created_at DESC);

-- Research tasks
CREATE TABLE research_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    objective TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    agent VARCHAR(100) NOT NULL,
    inputs JSONB DEFAULT '{}',
    depends_on JSONB DEFAULT '[]',
    priority INTEGER DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    result JSONB
);

CREATE INDEX idx_research_tasks_job_id ON research_tasks(job_id);
CREATE INDEX idx_research_tasks_status ON research_tasks(status);

-- Sources
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    url TEXT,
    title TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    content_hash VARCHAR(64),
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sources_job_id ON sources(job_id);

-- Evidence
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    claim TEXT NOT NULL,
    supporting_text TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    verification_status VARCHAR(50) DEFAULT 'unverified',
    verification_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_job_id ON evidence(job_id);
CREATE INDEX idx_evidence_source_id ON evidence(source_id);

-- Documents (uploaded/ingested)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES research_jobs(id) ON DELETE SET NULL,
    filename VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    file_size INTEGER,
    file_path VARCHAR(1000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_job_id ON documents(job_id);

-- Document chunks (for RAG)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(768),  -- Requires pgvector extension
    metadata JSONB DEFAULT '{}',
    chunk_index INTEGER NOT NULL,
    start_char INTEGER,
    end_char INTEGER
);

CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    executive_summary TEXT,
    methodology TEXT,
    findings JSONB DEFAULT '[]',
    evidence_ids JSONB DEFAULT '[]',
    source_ids JSONB DEFAULT '[]',
    conclusions JSONB DEFAULT '[]',
    limitations JSONB DEFAULT '[]',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent execution traces
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    task_id UUID REFERENCES research_tasks(id) ON DELETE SET NULL,
    agent_name VARCHAR(100) NOT NULL,
    request_id UUID NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    success BOOLEAN,
    input JSONB,
    output JSONB,
    tool_calls JSONB DEFAULT '[]',
    model_calls JSONB DEFAULT '[]',
    errors JSONB DEFAULT '[]',
    duration_ms INTEGER
);

CREATE INDEX idx_agent_runs_job_id ON agent_runs(job_id);
CREATE INDEX idx_agent_runs_task_id ON agent_runs(task_id);

-- Model call logs
CREATE TABLE model_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_run_id UUID REFERENCES agent_runs(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## SQLAlchemy Models

```python
# packages/database/models/research_job.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class ResearchJob(Base):
    __tablename__ = "research_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), nullable=False)
    question = Column(Text, nullable=False)
    objective = Column(Text, nullable=False)
    domain = Column(String(255))
    scope = Column(Text)
    constraints = Column(JSONB, default=list)
    expected_output = Column(String(100), default="report")
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    tasks = relationship("ResearchTask", back_populates="job", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="job", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="job", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="job")
    reports = relationship("Report", back_populates="job", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="job", cascade="all, delete-orphan")

class ResearchTask(Base):
    __tablename__ = "research_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False)
    objective = Column(Text, nullable=False)
    context = Column(JSONB, default=dict)
    agent = Column(String(100), nullable=False)
    inputs = Column(JSONB, default=dict)
    depends_on = Column(JSONB, default=list)
    priority = Column(Integer, default=1)
    status = Column(String(50), nullable=False, default="pending")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    result = Column(JSONB)
    
    job = relationship("ResearchJob", back_populates="tasks")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    url = Column(Text)
    title = Column(Text, nullable=False)
    metadata = Column(JSONB, default=dict)
    content_hash = Column(String(64))
    retrieved_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    job = relationship("ResearchJob", back_populates="sources")
    evidence = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    claim = Column(Text, nullable=False)
    supporting_text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.5)
    verification_status = Column(String(50), default="unverified")
    verification_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    job = relationship("ResearchJob", back_populates="evidence")
    source = relationship("Source", back_populates="evidence")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="SET NULL"))
    filename = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    content = Column(Text)
    metadata = Column(JSONB, default=dict)
    file_size = Column(Integer)
    file_path = Column(String(1000))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    job = relationship("ResearchJob", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    # embedding = Column(Vector(768))  # Requires pgvector
    metadata = Column(JSONB, default=dict)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer)
    end_char = Column(Integer)
    
    document = relationship("Document", back_populates="chunks")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    executive_summary = Column(Text)
    methodology = Column(Text)
    findings = Column(JSONB, default=list)
    evidence_ids = Column(JSONB, default=list)
    source_ids = Column(JSONB, default=list)
    conclusions = Column(JSONB, default=list)
    limitations = Column(JSONB, default=list)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    job = relationship("ResearchJob", back_populates="reports")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("research_tasks.id", ondelete="SET NULL"))
    agent_name = Column(String(100), nullable=False)
    request_id = Column(UUID(as_uuid=True), nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    success = Column(Boolean)
    input = Column(JSONB)
    output = Column(JSONB)
    tool_calls = Column(JSONB, default=list)
    model_calls = Column(JSONB, default=list)
    errors = Column(JSONB, default=list)
    duration_ms = Column(Integer)
    
    job = relationship("ResearchJob", back_populates="agent_runs")
    model_calls = relationship("ModelCall", back_populates="agent_run", cascade="all, delete-orphan")

class ModelCall(Base):
    __tablename__ = "model_calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"))
    provider = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    request_type = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    latency_ms = Column(Integer)
    success = Column(Boolean)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    agent_run = relationship("AgentRun", back_populates="model_calls")
```

## ChromaDB Collections

```python
# packages/retrieval/chroma_store.py
import chromadb
from chromadb.config import Settings
from packages.retrieval.vector_store import VectorStore, VectorDocument
from packages.shared.config import settings

class ChromaStore(VectorStore):
    """ChromaDB vector store implementation."""
    
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collections = {}
    
    def _get_collection(self, name: str):
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[name]
    
    async def add(self, documents: list[VectorDocument]) -> None:
        collection = self._get_collection("documents")
        
        collection.add(
            ids=[d.id for d in documents],
            embeddings=[d.embedding for d in documents],
            documents=[d.content for d in documents],
            metadatas=[d.metadata for d in documents],
        )
    
    async def query(
        self,
        collection: str,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict | None = None,
    ) -> list[VectorDocument]:
        col = self._get_collection(collection)
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )
        
        return [
            VectorDocument(
                id=results["ids"][0][i],
                content=results["documents"][0][i],
                embedding=results["embeddings"][0][i] if results["embeddings"] else None,
                metadata=results["metadatas"][0][i],
                distance=results["distances"][0][i] if results["distances"] else None,
            )
            for i in range(len(results["ids"][0]))
        ]
    
    async def delete(self, collection: str, ids: list[str]) -> None:
        self._get_collection(collection).delete(ids=ids)
    
    async def health_check(self) -> bool:
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False
```

## Repository Pattern

```python
# packages/database/repositories/research_job_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from packages.database.models.research_job import ResearchJob, ResearchTask, Source, Evidence
from typing import Optional, List
import uuid

class ResearchJobRepository:
    """Repository for research job operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, job: ResearchJob) -> ResearchJob:
        self.session.add(job)
        await self.session.flush()
        return job
    
    async def get(self, job_id: uuid.UUID) -> Optional[ResearchJob]:
        result = await self.session.execute(
            select(ResearchJob).where(ResearchJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_relations(self, job_id: uuid.UUID) -> Optional[ResearchJob]:
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
    
    async def update_status(self, job_id: uuid.UUID, status: str, error: str | None = None) -> None:
        values = {"status": status, "updated_at": datetime.utcnow()}
        if error:
            values["error_message"] = error
        if status == "completed":
            values["completed_at"] = datetime.utcnow()
        
        await self.session.execute(
            update(ResearchJob).where(ResearchJob.id == job_id).values(**values)
        )
        await self.session.flush()
    
    async def list_jobs(self, limit: int = 50, offset: int = 0) -> List[ResearchJob]:
        result = await self.session.execute(
            select(ResearchJob)
            .order_by(ResearchJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

class TaskRepository:
    """Repository for task operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, task: ResearchTask) -> ResearchTask:
        self.session.add(task)
        await self.session.flush()
        return task
    
    async def get(self, task_id: uuid.UUID) -> Optional[ResearchTask]:
        result = await self.session.execute(
            select(ResearchTask).where(ResearchTask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, task_id: uuid.UUID, status: TaskStatus, error: str | None = None) -> None:
        values = {"status": status.value}
        if status == TaskStatus.RUNNING:
            values["started_at"] = datetime.utcnow()
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            values["completed_at"] = datetime.utcnow()
        if error:
            values["error_message"] = error
        
        await self.session.execute(
            update(ResearchTask).where(ResearchTask.id == task_id).values(**values)
        )
        await self.session.flush()
```

## Connection Management

```python
# packages/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from packages.shared.config import settings
from contextlib import asynccontextmanager

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.log_level == "DEBUG",
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    await engine.dispose()
```

## Migration Strategy

```bash
# Using Alembic for migrations
# packages/database/migrations/

alembic.ini
env.py
versions/
    001_initial_schema.py
    002_add_vector_support.py
    ...
```

```python
# packages/database/migrations/env.py
from packages.database.connection import Base
from packages.database.models import *  # Import all models
target_metadata = Base.metadata
```

---

*Database layer uses repository pattern for testability - swap implementations for testing.*