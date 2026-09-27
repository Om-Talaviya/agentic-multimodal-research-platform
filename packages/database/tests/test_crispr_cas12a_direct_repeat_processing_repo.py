"""Tests for Phase 227: Autonomous CRISPR-Cas12a Multiplex crRNA Array Self-Processing & Asymmetric Cleavage Engine Repo."""

import pytest
from database.repositories.crispr_cas12a_direct_repeat_processing_repo import CrisprCas12aDirectRepeatProcessingRepository


@pytest.mark.asyncio
async def test_crispr_cas12a_direct_repeat_processing_repository(db_session):
    repo = CrisprCas12aDirectRepeatProcessingRepository(db_session)

    study = await repo.create_study(
        name="Study_227_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-cas12a-direct-repeat-processing",
        crrna_processing_efficiency_pct=98.2,
        collateral_ssdna_trans_cleavage_rate=8400.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 227 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_227_Verification"
    assert getattr(study, "crrna_processing_efficiency_pct") == 98.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AsCas12a_Quad_crRNA_Array_PolyA_Cassette",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "AsCas12a_Quad_crRNA_Array_PolyA_Cassette"

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
    assert fetched.name == "Study_227_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
