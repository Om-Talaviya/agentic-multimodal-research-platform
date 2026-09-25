"""Tests for Phase 192: Cryo-EM Continuous Conformational Heterogeneity & Manifold Engine Repo."""

import pytest
from database.repositories.cryoem_manifold_dynamics_repo import CryoEMManifoldDynamicsRepository


@pytest.mark.asyncio
async def test_cryoem_manifold_dynamics_repository(db_session):
    repo = CryoEMManifoldDynamicsRepository(db_session)

    study = await repo.create_study(
        name="Study_192_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Cryo-EM Manifold Dynamics",
        latent_manifold_eigenvalue_variance=74.5,
        free_energy_barrier_kcal_mol=3.24,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 192 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_192_Verification"
    assert getattr(study, "latent_manifold_eigenvalue_variance") == 74.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Conformational State A (Open Active Pocket)",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Conformational State A (Open Active Pocket)"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_192_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
