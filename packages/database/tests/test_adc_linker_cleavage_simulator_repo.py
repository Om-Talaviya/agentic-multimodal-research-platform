"""Tests for Phase 361: Autonomous Target-Activated Pro-Drug (ADC/PDC) Cleavable Linker Hydrolysis & Payload Release Simulator Repo."""

import pytest
from database.repositories.adc_linker_cleavage_simulator_repo import AdcLinkerCleavageSimulatorRepository


@pytest.mark.asyncio
async def test_adc_linker_cleavage_simulator_repository(db_session):
    repo = AdcLinkerCleavageSimulatorRepository(db_session)

    study = await repo.create_study(
        name="Study_361_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="adc-linker-cleavage-simulator",
        intracellular_payload_release_efficiency_pct=94.5,
        plasma_circulation_premature_leakage_rate_pct_day=0.45,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 361 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_361_Verification"
    assert getattr(study, "intracellular_payload_release_efficiency_pct") == 94.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="HER2_Targeted_Trastuzumab_Deruxtecan_Topoisomerase_I_ADC",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "HER2_Targeted_Trastuzumab_Deruxtecan_Topoisomerase_I_ADC"

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
    assert fetched.name == "Study_361_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
