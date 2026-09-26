"""Tests for Phase 216: Autonomous Targeted Covalent Inhibitor (TCI) Electrophilic Warhead Reactivity & Cysteine Residence Time Engine Repo."""

import pytest
from database.repositories.targeted_covalent_inhibitor_warhead_repo import TargetedCovalentInhibitorWarheadRepository


@pytest.mark.asyncio
async def test_targeted_covalent_inhibitor_warhead_repository(db_session):
    repo = TargetedCovalentInhibitorWarheadRepository(db_session)

    study = await repo.create_study(
        name="Study_216_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="targeted-covalent-inhibitor-warhead",
        kinact_over_ki_M_s=48500.0,
        cysteine_residence_time_hours=72.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 216 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_216_Verification"
    assert getattr(study, "kinact_over_ki_M_s") == 48500.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="EGFR_C797S_Acrylamide_Warhead_CandidateA",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "EGFR_C797S_Acrylamide_Warhead_CandidateA"

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
    assert fetched.name == "Study_216_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
