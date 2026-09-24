"""Tests for MilestoneV18Repository (Phase 154)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.milestone_v1_8_repo import MilestoneV18Repository


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_milestone_v1_8_repo_lifecycle(async_db: AsyncSession):
    repo = MilestoneV18Repository(async_db)

    orch = await repo.create_orchestration(
        orchestration_name="Milestone v1.8 Synthesis Test",
        milestone_version="v1.8",
        total_phases_integrated=154,
        cross_domain_pipeline_status="SYNCHRONIZED",
        orchestration_confidence_score=0.99,
        global_system_entropy=0.012,
    )
    assert orch.id is not None

    await repo.add_workflow_node(
        orchestration_id=orch.id,
        node_name="Spatial RNA Velocity",
        domain_category="Spatial",
        phase_reference="Phase 146",
        execution_latency_ms=15.0,
        node_fidelity_score=0.99,
    )

    await repo.add_executive_report(
        orchestration_id=orch.id,
        report_title="Synthesis Report",
        executive_summary="Summary text",
        primary_breakthrough="Breakthrough discovery",
        recommended_clinical_translation="Preclinical testing",
    )

    loaded = await repo.get_orchestration_with_details(orch.id)
    assert loaded is not None
    assert len(loaded.workflow_nodes) == 1
    assert len(loaded.synthesis_reports) == 1
