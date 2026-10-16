"""Tests for Phase 572: Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.optogenetic_neuromodulatory_gpc_receptor_activator_repo import OptogeneticNeuromodulatoryGpcReceptorActivatorRepository


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
async def test_optogenetic_neuromodulatory_gpc_receptor_activator_repository(async_session: AsyncSession):
    repo = OptogeneticNeuromodulatoryGpcReceptorActivatorRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor Benchmark",
        target_specimen="Opto-beta2-Adrenergic Receptor Chimeric Constructs Expressed in Primary Hippocampal Neurons",
        analytical_modality="opto-gpcr-second-messenger-modeling",
        camp_generation_rate_nm_s=42.5,
        g_protein_coupling_selectivity=0.965,
        photocurrent_deactivation_tau_ms=145.0,
        downstream_phosphorylation_index=0.912,
        confidence_score=0.995,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor Benchmark"
    assert study.camp_generation_rate_nm_s == 42.5
    assert study.confidence_score == 0.995

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Opto_GPCR_Coupled_Signaling_Cascade",
        quantitative_value=42.5,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Opto_GPCR_Coupled_Signaling_Cascade"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="camp_generation_rate_nm_s",
        observed_value=42.5,
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
