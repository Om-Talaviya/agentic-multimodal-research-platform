"""Tests for Phase 340: Autonomous CRISPR Non-Homologous End Joining (NHEJ) vs HDR Repair Outcome Probability Forecaster Repo."""

import pytest
from database.repositories.crispr_repair_outcome_forecaster_repo import CrisprRepairOutcomeForecasterRepository


@pytest.mark.asyncio
async def test_crispr_repair_outcome_forecaster_repository(db_session):
    repo = CrisprRepairOutcomeForecasterRepository(db_session)

    study = await repo.create_study(
        name="Study_340_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-repair-forecaster",
        predicted_repair_profile_accuracy_pct=91.2,
        precision_in_frame_editing_frequency_pct=84.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 340 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_340_Verification"
    assert getattr(study, "predicted_repair_profile_accuracy_pct") == 91.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sickle_Cell_HBB_Gene_Correction_HDR_vs_NHEJ_Distribution",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Sickle_Cell_HBB_Gene_Correction_HDR_vs_NHEJ_Distribution"

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
    assert fetched.name == "Study_340_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
