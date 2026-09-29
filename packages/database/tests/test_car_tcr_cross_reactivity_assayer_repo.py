"""Tests for Phase 339: Autonomous CAR-T TCR-pMHC Cross-Reactivity & Structural Off-Target Immunotoxicity Assayer Repo."""

import pytest
from database.repositories.car_tcr_cross_reactivity_assayer_repo import CarTcrCrossReactivityAssayerRepository


@pytest.mark.asyncio
async def test_car_tcr_cross_reactivity_assayer_repository(db_session):
    repo = CarTcrCrossReactivityAssayerRepository(db_session)

    study = await repo.create_study(
        name="Study_339_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="car-tcr-cross-reactivity",
        self_epitope_cross_reactivity_safety_index=99.4,
        off_target_binding_free_energy_delta_g_score=4.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 339 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_339_Verification"
    assert getattr(study, "self_epitope_cross_reactivity_safety_index") == 99.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="NY_ESO_1_Engineered_TCR_Titin_Cross_Reactivity_Filter",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "NY_ESO_1_Engineered_TCR_Titin_Cross_Reactivity_Filter"

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
    assert fetched.name == "Study_339_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
