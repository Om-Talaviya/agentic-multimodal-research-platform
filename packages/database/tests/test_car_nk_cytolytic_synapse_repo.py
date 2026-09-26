"""Tests for Phase 198: CAR-NK Immune Synapse & Cytolytic Kinetics Simulator Repo."""

import pytest
from database.repositories.car_nk_cytolytic_synapse_repo import CARNKCytolyticSynapseRepository


@pytest.mark.asyncio
async def test_car_nk_cytolytic_synapse_repository(db_session):
    repo = CARNKCytolyticSynapseRepository(db_session)

    study = await repo.create_study(
        name="Study_198_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="CAR-NK Cytolytic Synapse",
        cytolytic_specific_lysis_percent=92.6,
        synapse_polarization_time_minutes=18.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 198 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_198_Verification"
    assert getattr(study, "cytolytic_specific_lysis_percent") == 92.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Dual-CAR-NK (anti-CD19 / anti-CD22) Construct",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Dual-CAR-NK (anti-CD19 / anti-CD22) Construct"

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
    assert fetched.name == "Study_198_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
