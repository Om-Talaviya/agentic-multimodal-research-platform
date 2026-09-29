"""Tests for Phase 289: Autonomous Spatial Multi-Omics Whole-Transcriptome In-Situ Sequencing (ISS) Padlock Decoding Engine Repo."""

import pytest
from database.repositories.iss_padlock_rolling_circle_repo import IssPadlockRollingCircleRepository


@pytest.mark.asyncio
async def test_iss_padlock_rolling_circle_repository(db_session):
    repo = IssPadlockRollingCircleRepository(db_session)

    study = await repo.create_study(
        name="Study_289_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="iss-padlock-rolling-circle",
        optical_decoding_accuracy_pct=98.4,
        subcellular_rca_puncta_density_per_100um2=48.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 289 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_289_Verification"
    assert getattr(study, "optical_decoding_accuracy_pct") == 98.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Human_Cerebral_Cortex_Targeted_ISS_Puncta_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Human_Cerebral_Cortex_Targeted_ISS_Puncta_Map"

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
    assert fetched.name == "Study_289_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
