"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

TestBase = declarative_base()


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create test database session."""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_research_job():
    """Create a sample research job."""
    from database.models import ResearchJob
    return ResearchJob(
        request_id="00000000-0000-0000-0000-000000000001",
        question="What is quantum computing?",
        objective="Explain quantum computing basics",
        domain="computer science",
        scope="general overview",
        constraints=["peer-reviewed sources"],
        expected_output="report",
        status="pending",
    )


@pytest.fixture
def sample_task():
    """Create a sample task."""
    from database.models import ResearchTask
    return ResearchTask(
        job_id="00000000-0000-0000-0000-000000000001",
        type="web_research",
        objective="Search for quantum computing articles",
        agent="web_research",
        status="pending",
    )