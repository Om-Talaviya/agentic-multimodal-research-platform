"""Tests for Phase 433: Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine Repo."""

import pytest
from database.repositories.synchrotron_saxs_ensemble_fitter_repo import SynchrotronSaxsEnsembleFitterRepository


@pytest.mark.asyncio
async def test_synchrotron_saxs_ensemble_fitter_repository(db_session):
    repo = SynchrotronSaxsEnsembleFitterRepository(db_session)

    study = await repo.create_study(
        name="Study_433_Verification",
        target_specimen="Intrinsically Disordered Kinase Domain in Solution",
        analytical_modality="synchrotron-saxs",
        radius_of_gyration_Rg_angstrom=34.2,
        kratky_plot_flexibility_index=0.895,
        ensemble_fit_chi_squared=1.08,
        maximum_particle_dimension_Dmax_angstrom=112.0,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 433 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_433_Verification"
    assert study.radius_of_gyration_Rg_angstrom == 34.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Guinier_Region_Rg_Disorder_Ensemble",
        profile_category="Primary Step",
        quantitative_value=34.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Guinier_Region_Rg_Disorder_Ensemble"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="radius_of_gyration_Rg_angstrom",
        observed_value=34.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 34.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_433_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
