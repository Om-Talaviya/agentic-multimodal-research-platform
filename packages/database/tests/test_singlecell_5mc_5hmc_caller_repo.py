"""Tests for Phase 381: Autonomous Single-Cell DNA Methylation and Hydroxymethylation (5mC/5hmC) Bisulfite-Free Caller Repo."""

import pytest
from database.repositories.singlecell_5mc_5hmc_caller_repo import Singlecell5mc5hmcCallerRepository


@pytest.mark.asyncio
async def test_singlecell_5mc_5hmc_caller_repository(db_session):
    repo = Singlecell5mc5hmcCallerRepository(db_session)

    study = await repo.create_study(
        name="Study_381_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="singlecell-5mc-5hmc-caller",
        base_resolution_5hmc_calling_precision_pct=98.4,
        single_cell_cpg_site_coverage_depth_fold=12.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 381 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_381_Verification"
    assert getattr(study, "base_resolution_5hmc_calling_precision_pct") == 98.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Embryonic_Stem_Cell_Pluripotency_5hmC_Epigenomic_Atlas",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Embryonic_Stem_Cell_Pluripotency_5hmC_Epigenomic_Atlas"

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
    assert fetched.name == "Study_381_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
