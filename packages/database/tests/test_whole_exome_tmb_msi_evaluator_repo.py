"""Tests for Phase 400: Autonomous Whole-Exome Tumor Mutational Burden & Microsatellite Instability Evaluator Repo."""

import pytest
from database.repositories.whole_exome_tmb_msi_evaluator_repo import WholeExomeTmbMsiEvaluatorRepository


@pytest.mark.asyncio
async def test_whole_exome_tmb_msi_evaluator_repository(db_session):
    repo = WholeExomeTmbMsiEvaluatorRepository(db_session)

    study = await repo.create_study(
        name="Study_400_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="whole-exome-tmb-msi-evaluation",
        tumor_mutational_burden_mut_per_megabase=24.6,
        msi_high_classification_confidence_pct=99.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 400 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_400_Verification"
    assert getattr(study, "tumor_mutational_burden_mut_per_megabase") == 24.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Mismatch_Repair_MLH1_MSH2_Germline_Somatic_Variant_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Mismatch_Repair_MLH1_MSH2_Germline_Somatic_Variant_Matrix"

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
    assert fetched.name == "Study_400_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
