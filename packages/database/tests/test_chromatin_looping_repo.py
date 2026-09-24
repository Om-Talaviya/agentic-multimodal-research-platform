"""Tests for ChromatinLoopRepository (Phase 152)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.chromatin_looping_repo import ChromatinLoopRepository


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
async def test_chromatin_looping_repo_lifecycle(async_db: AsyncSession):
    repo = ChromatinLoopRepository(async_db)

    study = await repo.create_study(
        cell_line_name="GM12878",
        chromosome="chr1",
        genomic_resolution_bp=5000,
        total_loops_detected=120,
        tad_count=45,
        mean_insulation_score=0.91,
        mean_loop_span_kb=150.0,
    )
    assert study.id is not None

    await repo.add_contact_edge(
        study_id=study.id,
        enhancer_locus="chr1:10000-12000",
        target_gene="CDK1",
        contact_frequency=25.0,
        loop_span_bp=80000,
        ctcf_convergent_motif=True,
        activation_log2fc=2.1,
    )

    await repo.add_tad_boundary(
        study_id=study.id,
        start_bp=50000,
        end_bp=55000,
        insulation_score=0.92,
        ctcf_occupancy_score=150.0,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.contact_edges) == 1
    assert len(loaded.tad_boundaries) == 1
