"""Tests for Single-Molecule FRET (smFRET) Kinetics repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.smfret_repo import SmFRETRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_experiment(async_session: AsyncSession):
    repo = SmFRETRepository(async_session)

    exp = await repo.create_experiment(
        experiment_title="Hsp90 Conformational Switching",
        macromolecule_name="Hsp90 Chaperone Dimer",
        donor_fluorophore="Cy3",
        acceptor_fluorophore="Cy5",
        forster_radius_angstrom=54.0,
        acquisition_rate_hz=100.0,
        total_molecules_recorded=42,
        state_count=3,
        experiment_metadata_json={"gamma_factor": 1.0, "crosstalk_beta": 0.05},
    )

    assert exp.id is not None
    assert exp.experiment_title == "Hsp90 Conformational Switching"

    fetched = await repo.get_experiment(exp.id)
    assert fetched is not None
    assert fetched.donor_fluorophore == "Cy3"
    assert fetched.total_molecules_recorded == 42


@pytest.mark.asyncio
async def test_add_traces_and_states(async_session: AsyncSession):
    repo = SmFRETRepository(async_session)

    exp = await repo.create_experiment(
        experiment_title="Riboswitch Folding",
        macromolecule_name="SAM-I Riboswitch",
        donor_fluorophore="Cy3",
        acceptor_fluorophore="Cy5",
    )

    traces_data = [
        {
            "molecule_index": 1,
            "total_frames": 200,
            "mean_fret_efficiency": 0.45,
            "photobleaching_frame": 180,
            "trace_data_json": [{"frame": 0, "fret_eff": 0.2}, {"frame": 1, "fret_eff": 0.7}],
        }
    ]

    traces = await repo.add_traces(exp.id, traces_data)
    assert len(traces) == 1
    assert traces[0].mean_fret_efficiency == 0.45

    states_data = [
        {
            "state_index": 0,
            "state_name": "OPEN",
            "mean_efficiency": 0.18,
            "occupancy_fraction": 0.35,
            "mean_dwell_time_ms": 120.0,
            "transition_rates_json": {"1": 6.2, "2": 1.8},
        },
        {
            "state_index": 1,
            "state_name": "CLOSED",
            "mean_efficiency": 0.84,
            "occupancy_fraction": 0.65,
            "mean_dwell_time_ms": 160.0,
            "transition_rates_json": {"0": 3.4},
        },
    ]

    states = await repo.add_states(exp.id, states_data)
    assert len(states) == 2

    fetched_traces = await repo.get_traces_by_experiment(exp.id)
    assert len(fetched_traces) == 1

    fetched_states = await repo.get_states_by_experiment(exp.id)
    assert len(fetched_states) == 2
