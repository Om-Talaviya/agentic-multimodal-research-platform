"""Tests for Phase 577: Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.microfluidic_droplet_directed_evolution_repo import MicrofluidicDropletDirectedEvolutionRepository


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
async def test_microfluidic_droplet_directed_evolution_repository(async_session: AsyncSession):
    repo = MicrofluidicDropletDirectedEvolutionRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator Benchmark",
        target_specimen="Picoliter Water-in-Oil Droplet Encapsulated TEM-1 β-Lactamase Saturation Mutagenesis Library",
        analytical_modality="microfluidic-droplet-directed-evolution",
        droplet_generation_rate_hz=12500.0,
        enzyme_kcat_fold_improvement=8.4,
        fitness_landscape_ruggedness_index=0.62,
        epistatic_interaction_coefficient=0.38,
        confidence_score=0.996,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator Benchmark"
    assert study.droplet_generation_rate_hz == 12500.0
    assert study.confidence_score == 0.996

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Droplet_Encapsulation_Variant_Frequency_Distribution",
        quantitative_value=13125.0,
        profile_category="Primary Profile",
        log2_fold_change=1.92,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Droplet_Encapsulation_Variant_Frequency_Distribution"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="droplet_generation_rate_hz",
        observed_value=12500.0,
        z_score=2.92,
        p_value=0.001,
    )
    assert trace.id is not None
    assert trace.study_id == study.id

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.id == study.id

    studies = await repo.list_studies()
    assert len(studies) >= 1
