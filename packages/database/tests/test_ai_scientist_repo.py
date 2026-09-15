"""Unit tests for AI Scientist Repository (Phase 50)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.ai_scientist_repo import AutonomousScientistRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_ai_scientist_repo_crud(async_session: AsyncSession):
    repo = AutonomousScientistRepository(async_session)
    program = await repo.create_program(
        title="Autonomous Oncogenic Discovery",
        research_domain="Oncology",
        goal_statement="Discover dual degraders",
        max_cycles=3
    )
    assert program.id is not None
    assert program.status == "BREAKTHROUGH_ACHIEVED"

    cycle = await repo.add_cycle(
        program_id=program.id,
        cycle_index=1,
        hypothesis="Initial kinase feedback",
        experimental_protocol="RNA-seq and phospho-proteomics",
        simulation_metrics={"confidence": 0.9},
        metacognitive_reflection="Observed bypass reactivation",
        novelty_delta=0.15
    )
    assert cycle.id is not None

    bt = await repo.add_breakthrough(
        program_id=program.id,
        title="Novel Macrocyclic Degrader",
        breakthrough_class="NOBEL_TURING_CLASS",
        novelty_score=0.96,
        empirical_validity=0.92,
        falsifiability=0.88,
        formal_conclusion="Synthetic lethality achieved",
        whitepaper_summary="Comprehensive report"
    )
    assert bt.id is not None

    fetched = await repo.get_program(program.id)
    assert len(fetched.iteration_cycles) == 1
    assert len(fetched.breakthroughs) == 1
