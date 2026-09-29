"""Tests for Phase 360: Autonomous Proteome-Wide Native Mass Spectrometry (Native MS) Non-Covalent Complex Stoichiometry Resolver Repo."""

import pytest
from database.repositories.native_ms_complex_stoichiometry_repo import NativeMsComplexStoichiometryRepository


@pytest.mark.asyncio
async def test_native_ms_complex_stoichiometry_repository(db_session):
    repo = NativeMsComplexStoichiometryRepository(db_session)

    study = await repo.create_study(
        name="Study_360_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="native-ms-complex-stoichiometry",
        quaternary_mass_determination_accuracy_ppm=12.0,
        charge_state_deconvolution_confidence_score=99.1,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 360 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_360_Verification"
    assert getattr(study, "quaternary_mass_determination_accuracy_ppm") == 12.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Intact_Ribosome_70S_Quaternary_Native_MS_Spectrum",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Intact_Ribosome_70S_Quaternary_Native_MS_Spectrum"

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
    assert fetched.name == "Study_360_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
