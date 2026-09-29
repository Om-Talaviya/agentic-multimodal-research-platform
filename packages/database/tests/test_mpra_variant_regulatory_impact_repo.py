"""Tests for Phase 283: Autonomous Ultra-Deep Massively Parallel Reporter Assay (MPRA) Variant Regulatory Impact Predictor Repo."""

import pytest
from database.repositories.mpra_variant_regulatory_impact_repo import MpraVariantRegulatoryImpactRepository


@pytest.mark.asyncio
async def test_mpra_variant_regulatory_impact_repository(db_session):
    repo = MpraVariantRegulatoryImpactRepository(db_session)

    study = await repo.create_study(
        name="Study_283_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mpra-variant-regulatory-impact",
        mpra_expression_fold_change_r2=0.91,
        causal_regulatory_variant_detection_power=96.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 283 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_283_Verification"
    assert getattr(study, "mpra_expression_fold_change_r2") == 0.91

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Autoimmune_GWAS_Non_Coding_Enhancer_MPRA_Screen",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Autoimmune_GWAS_Non_Coding_Enhancer_MPRA_Screen"

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
    assert fetched.name == "Study_283_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
