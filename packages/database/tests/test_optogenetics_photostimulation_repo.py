"""Tests for Phase 210: Autonomous Optogenetic Photostimulation Pattern Synthesis & Neuronal Spike Raster Forecaster Engine Repo."""

import pytest
from database.repositories.optogenetics_photostimulation_repo import OptogeneticsPhotostimulationRepository


@pytest.mark.asyncio
async def test_optogenetics_photostimulation_repository(db_session):
    repo = OptogeneticsPhotostimulationRepository(db_session)

    study = await repo.create_study(
        name="Study_210_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optogenetics-photostimulation",
        spike_fidelity_pct=99.4,
        photocurrent_density_pA_um2=45.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 210 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_210_Verification"
    assert getattr(study, "spike_fidelity_pct") == 99.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CoAd_ChR2_H134R_Cortical_Layer5",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CoAd_ChR2_H134R_Cortical_Layer5"

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
    assert fetched.name == "Study_210_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
