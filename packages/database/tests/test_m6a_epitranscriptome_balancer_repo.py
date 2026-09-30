"""Tests for Phase 389: Autonomous Whole-Transcriptome m6A Methyltransferase & Demethylase Dynamic Balance Simulator Repo."""

import pytest
from database.repositories.m6a_epitranscriptome_balancer_repo import M6aEpitranscriptomeBalancerRepository


@pytest.mark.asyncio
async def test_m6a_epitranscriptome_balancer_repository(db_session):
    repo = M6aEpitranscriptomeBalancerRepository(db_session)

    study = await repo.create_study(
        name="Study_389_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="m6a-epitranscriptome-balancer",
        transcriptome_wide_m6a_stoichiometric_fidelity_pct=97.8,
        target_mrna_decay_half_life_modulation_fold=3.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 389 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_389_Verification"
    assert getattr(study, "transcriptome_wide_m6a_stoichiometric_fidelity_pct") == 97.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="METTL3_Overexpressed_Glioblastoma_Stem_Cell_m6A_Dynamic_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "METTL3_Overexpressed_Glioblastoma_Stem_Cell_m6A_Dynamic_Map"

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
    assert fetched.name == "Study_389_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
