"""Tests for Phase 568: Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.bacterial_chemotactic_micro_biohybrid_swimmer_repo import BacterialChemotacticMicroBiohybridSwimmerRepository


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_bacterial_chemotactic_micro_biohybrid_swimmer_repository(async_session: AsyncSession):
    repo = BacterialChemotacticMicroBiohybridSwimmerRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator Benchmark",
        target_specimen="Engineered Escherichia coli MG1655 Flagellar Micro-Biohybrid Swimmers in Attractant Aspartate Microfluidic Gradient",
        analytical_modality="bacterial-chemotactic-biohybrid-simulation",
        chemotactic_drift_velocity_um_s=18.5,
        run_tumble_frequency_ratio=4.2,
        target_accumulation_index=0.92,
        flagellar_motor_torque_efficiency=0.88,
        confidence_score=0.995,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator Benchmark"
    assert study.chemotactic_drift_velocity_um_s == 18.5
    assert study.confidence_score == 0.995

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Chemotactic_Biased_Random_Walk_Cluster",
        quantitative_value=18.5,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Chemotactic_Biased_Random_Walk_Cluster"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="chemotactic_drift_velocity_um_s",
        observed_value=18.5,
        z_score=2.85,
        p_value=0.001,
    )
    assert trace.id is not None
    assert trace.study_id == study.id

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.id == study.id

    studies = await repo.list_studies()
    assert len(studies) >= 1
