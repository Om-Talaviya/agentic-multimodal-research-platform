"""Tests for Phase 218: Autonomous Whole-Exome Sequencing (WES) Tumor Mutation Burden (TMB) & Microsatellite Instability (MSI) Ranker Engine Repo."""

import pytest
from database.repositories.whole_exome_tmb_msi_ranker_repo import WholeExomeTmbMsiRankerRepository


@pytest.mark.asyncio
async def test_whole_exome_tmb_msi_ranker_repository(db_session):
    repo = WholeExomeTmbMsiRankerRepository(db_session)

    study = await repo.create_study(
        name="Study_218_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="whole-exome-tmb-msi-ranker",
        tmb_mutations_per_mb=28.4,
        msi_instability_score_pct=94.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 218 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_218_Verification"
    assert getattr(study, "tmb_mutations_per_mb") == 28.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Colorectal_Adenocarcinoma_MSI_High_Hypermutated",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Colorectal_Adenocarcinoma_MSI_High_Hypermutated"

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
    assert fetched.name == "Study_218_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
