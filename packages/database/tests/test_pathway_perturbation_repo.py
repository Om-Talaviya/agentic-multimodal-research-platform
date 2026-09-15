"""Unit tests for Pathway Perturbation Repository (Phase 48)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.pathway_perturbation_repo import PathwayPerturbationRepository

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
async def test_pathway_perturbation_repo_crud(async_session: AsyncSession):
    repo = PathwayPerturbationRepository(async_session)
    exp = await repo.create_experiment(
        title="A549 KRAS Knockdown",
        cell_line="A549",
        perturbation_type="CRISPR_KO"
    )
    assert exp.id is not None
    assert exp.status == "SIMULATED"

    cascade = await repo.add_cascade(
        experiment_id=exp.id,
        pathway_name="MAPK/ERK",
        node_count=18,
        feedback_loops_count=3,
        steady_state_activation=0.75,
        cascade_topology={"upstream": ["EGFR"], "core": ["KRAS", "BRAF"]}
    )
    assert cascade.id is not None

    sim = await repo.add_simulation(
        experiment_id=exp.id,
        target_node="KRAS",
        inhibition_efficiency=94.0,
        downstream_phospho_delta=-80.0,
        metabolic_flux_shift=-50.0,
        time_course_hours=48,
        time_series_trajectories=[{"time_hours": 0, "target_activity": 1.0}],
        bypass_mechanisms=[{"bypass_pathway": "PI3K", "activation_delta_pct": 40.0}]
    )
    assert sim.id is not None

    fetched = await repo.get_experiment(exp.id)
    assert len(fetched.cascades) == 1
    assert len(fetched.simulations) == 1
