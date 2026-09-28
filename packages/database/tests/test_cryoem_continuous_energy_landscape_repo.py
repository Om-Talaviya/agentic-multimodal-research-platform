"""Tests for Phase 249: Autonomous Cryo-EM Continuous Heterogeneity Conformational Landscape & Energy Surface Reconstruction Engine Repo."""

import pytest
from database.repositories.cryoem_continuous_energy_landscape_repo import CryoemContinuousEnergyLandscapeRepository


@pytest.mark.asyncio
async def test_cryoem_continuous_energy_landscape_repository(db_session):
    repo = CryoemContinuousEnergyLandscapeRepository(db_session)

    study = await repo.create_study(
        name="Study_249_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-continuous-energy-landscape",
        latent_manifold_resolution_angstrom=2.4,
        conformational_transition_barrier_kcal_mol=4.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 249 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_249_Verification"
    assert getattr(study, "latent_manifold_resolution_angstrom") == 2.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ribosome_Pre_Translocation_Conformational_Manifold",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ribosome_Pre_Translocation_Conformational_Manifold"

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
    assert fetched.name == "Study_249_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
