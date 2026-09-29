"""Tests for Phase 325: Autonomous Tara-Oceans Scale Marine Microbial Metatranscriptomic Carbon Export & Nitrogen Flux Predictor Repo."""

import pytest
from database.repositories.ocean_metatranscriptome_carbon_flux_repo import OceanMetatranscriptomeCarbonFluxRepository


@pytest.mark.asyncio
async def test_ocean_metatranscriptome_carbon_flux_repository(db_session):
    repo = OceanMetatranscriptomeCarbonFluxRepository(db_session)

    study = await repo.create_study(
        name="Study_325_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="ocean-metatranscriptome-carbon-flux",
        carbon_export_flux_prediction_score_pct=93.5,
        particulate_organic_carbon_flux_mg_c_m2_day=240.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 325 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_325_Verification"
    assert getattr(study, "carbon_export_flux_prediction_score_pct") == 93.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Southern_Ocean_Diatom_Bloom_Carbon_Export_Transcriptome_Profile",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Southern_Ocean_Diatom_Bloom_Carbon_Export_Transcriptome_Profile"

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
    assert fetched.name == "Study_325_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
