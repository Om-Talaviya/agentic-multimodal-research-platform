"""Tests for Phase 573: Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.deep_learning_protein_protein_docking_affinity_repo import DeepLearningProteinProteinDockingAffinityRepository


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
async def test_deep_learning_protein_protein_docking_affinity_repository(async_session: AsyncSession):
    repo = DeepLearningProteinProteinDockingAffinityRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster Benchmark",
        target_specimen="SARS-CoV-2 Spike Receptor-Binding Domain Complexed with Engineered Nanobody Nb21-Fc Variant",
        analytical_modality="se3-diffusion-ppi-docking",
        interface_rmsd_angstrom=1.25,
        binding_free_energy_delta_g_kcal_mol=-14.8,
        docking_pose_confidence_plddt=92.4,
        buried_surface_area_angstrom2=1450.0,
        confidence_score=0.998,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster Benchmark"
    assert study.interface_rmsd_angstrom == 1.25
    assert study.confidence_score == 0.998

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Equivariant_Docked_Interface_Residue_Locus",
        quantitative_value=1.25,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Equivariant_Docked_Interface_Residue_Locus"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="interface_rmsd_angstrom",
        observed_value=1.25,
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
