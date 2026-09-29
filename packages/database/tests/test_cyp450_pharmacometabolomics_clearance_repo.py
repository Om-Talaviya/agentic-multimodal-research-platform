"""Tests for Phase 286: Autonomous Multi-Organ Pharmacometabolomics Drug Interaction & Cytochrome P450 Metabolic Clearance Simulator Repo."""

import pytest
from database.repositories.cyp450_pharmacometabolomics_clearance_repo import Cyp450PharmacometabolomicsClearanceRepository


@pytest.mark.asyncio
async def test_cyp450_pharmacometabolomics_clearance_repository(db_session):
    repo = Cyp450PharmacometabolomicsClearanceRepository(db_session)

    study = await repo.create_study(
        name="Study_286_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cyp450-pharmacometabolomics-clearance",
        cyp_intrinsic_clearance_prediction_accuracy=96.5,
        drug_drug_interaction_auc_ratio_error_pct=8.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 286 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_286_Verification"
    assert getattr(study, "cyp_intrinsic_clearance_prediction_accuracy") == 96.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ketoconazole_CYP3A4_Time_Dependent_Inhibition_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ketoconazole_CYP3A4_Time_Dependent_Inhibition_Model"

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
    assert fetched.name == "Study_286_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
