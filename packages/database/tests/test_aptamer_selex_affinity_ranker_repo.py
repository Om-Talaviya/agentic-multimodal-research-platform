"""Tests for Phase 394: In-Silico Systematic Evolution of Ligands (SELEX) Aptamer Affinity Ranker Repo."""

import pytest
from database.repositories.aptamer_selex_affinity_ranker_repo import AptamerSelexAffinityRankerRepository


@pytest.mark.asyncio
async def test_aptamer_selex_affinity_ranker_repository(db_session):
    repo = AptamerSelexAffinityRankerRepository(db_session)

    study = await repo.create_study(
        name="Study_394_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="aptamer-selex-affinity-ranking",
        aptamer_target_dissociation_constant_kd_nm=0.42,
        counter_selex_off_target_discrimination_ratio=145.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 394 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_394_Verification"
    assert getattr(study, "aptamer_target_dissociation_constant_kd_nm") == 0.42

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="2_Fluoropyrimidine_Modified_RNA_Aptamer_VEGF165_Lead",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "2_Fluoropyrimidine_Modified_RNA_Aptamer_VEGF165_Lead"

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
    assert fetched.name == "Study_394_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
