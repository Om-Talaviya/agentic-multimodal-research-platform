"""Tests for Phase 251: Autonomous CRISPR-Cas13 Collateral Cleavage & Viral RNA Detection Specificity Engine Repo."""

import pytest
from database.repositories.crispr_cas13_collateral_cleavage_repo import CrisprCas13CollateralCleavageRepository


@pytest.mark.asyncio
async def test_crispr_cas13_collateral_cleavage_repository(db_session):
    repo = CrisprCas13CollateralCleavageRepository(db_session)

    study = await repo.create_study(
        name="Study_251_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-cas13-collateral-cleavage",
        collateral_turnover_rate_kcat_km_s_M=12000000.0,
        mismatch_discrimination_ratio=48.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 251 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_251_Verification"
    assert getattr(study, "collateral_turnover_rate_kcat_km_s_M") == 12000000.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="SHERLOCK_Pan_Coronavirus_Cas13a_crRNA_Assay",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "SHERLOCK_Pan_Coronavirus_Cas13a_crRNA_Assay"

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
    assert fetched.name == "Study_251_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
