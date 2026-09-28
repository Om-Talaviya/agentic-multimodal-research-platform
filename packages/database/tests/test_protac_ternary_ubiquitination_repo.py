"""Tests for Phase 246: Autonomous Targeted Protein Degradation (PROTAC) Ternary Complex Cooperativity & Ubiquitination Kinetics Engine Repo."""

import pytest
from database.repositories.protac_ternary_ubiquitination_repo import ProtacTernaryUbiquitinationRepository


@pytest.mark.asyncio
async def test_protac_ternary_ubiquitination_repository(db_session):
    repo = ProtacTernaryUbiquitinationRepository(db_session)

    study = await repo.create_study(
        name="Study_246_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="protac-ternary-ubiquitination",
        ternary_cooperativity_alpha_factor=18.5,
        maximal_degradation_dmax_pct=94.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 246 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_246_Verification"
    assert getattr(study, "ternary_cooperativity_alpha_factor") == 18.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AR_V7_VHL_PROTAC_ARV110_Ternary_Equilibrium",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "AR_V7_VHL_PROTAC_ARV110_Ternary_Equilibrium"

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
    assert fetched.name == "Study_246_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
