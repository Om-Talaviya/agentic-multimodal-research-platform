"""Tests for Phase 345: Autonomous Chromatin Conformation Capture (Micro-C) Nucleosome-Resolution Loop Domain Caller Repo."""

import pytest
from database.repositories.micro_c_chromatin_loop_caller_repo import MicroCChromatinLoopCallerRepository


@pytest.mark.asyncio
async def test_micro_c_chromatin_loop_caller_repository(db_session):
    repo = MicroCChromatinLoopCallerRepository(db_session)

    study = await repo.create_study(
        name="Study_345_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="micro-c-chromatin-loops",
        chromatin_loop_detection_resolution_bp=200.0,
        loop_enrichment_over_local_background_fold=6.85,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 345 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_345_Verification"
    assert getattr(study, "chromatin_loop_detection_resolution_bp") == 200.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Human_ES_Cell_High_Resolution_Micro_C_Loop_Domain_Atlas",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Human_ES_Cell_High_Resolution_Micro_C_Loop_Domain_Atlas"

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
    assert fetched.name == "Study_345_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
