"""Tests for Phase 390: Autonomous Allosteric Cryptic Pocket Transient Opening & Molecular Dynamics Markov State Modeler Repo."""

import pytest
from database.repositories.allosteric_cryptic_pocket_msm_repo import AllostericCrypticPocketMsmRepository


@pytest.mark.asyncio
async def test_allosteric_cryptic_pocket_msm_repository(db_session):
    repo = AllostericCrypticPocketMsmRepository(db_session)

    study = await repo.create_study(
        name="Study_390_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="allosteric-cryptic-pocket-msm",
        cryptic_pocket_opening_transition_timescale_ns=450.0,
        pocket_druggability_score_site_map=1.18,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 390 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_390_Verification"
    assert getattr(study, "cryptic_pocket_opening_transition_timescale_ns") == 450.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="KRAS_Switch_II_Allosteric_Cryptic_Pocket_Markov_Transition_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "KRAS_Switch_II_Allosteric_Cryptic_Pocket_Markov_Transition_Matrix"

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
    assert fetched.name == "Study_390_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
