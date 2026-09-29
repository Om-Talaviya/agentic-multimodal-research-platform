"""Tests for Phase 293: Autonomous Non-Viral Lipid Nanoparticle (LNP) Endosomal Escape Kinetics & Bioavailability Forecaster Repo."""

import pytest
from database.repositories.lnp_endosomal_escape_kinetics_repo import LnpEndosomalEscapeKineticsRepository


@pytest.mark.asyncio
async def test_lnp_endosomal_escape_kinetics_repository(db_session):
    repo = LnpEndosomalEscapeKineticsRepository(db_session)

    study = await repo.create_study(
        name="Study_293_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="lnp-endosomal-escape-kinetics",
        cytosolic_payload_escape_efficiency_pct=14.8,
        endosomal_rupture_half_time_minutes=35.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 293 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_293_Verification"
    assert getattr(study, "cytosolic_payload_escape_efficiency_pct") == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="SM102_Ionizable_Lipid_Endosomal_Pore_Kinetics",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "SM102_Ionizable_Lipid_Endosomal_Pore_Kinetics"

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
    assert fetched.name == "Study_293_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
