"""Tests for Phase 359: Autonomous Synthetic Gene Drive Ecological Population Dynamics & CRISPR Escape Risk Forecaster Repo."""

import pytest
from database.repositories.gene_drive_ecological_risk_repo import GeneDriveEcologicalRiskRepository


@pytest.mark.asyncio
async def test_gene_drive_ecological_risk_repository(db_session):
    repo = GeneDriveEcologicalRiskRepository(db_session)

    study = await repo.create_study(
        name="Study_359_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="gene-drive-ecological-risk",
        target_population_suppression_pct=99.8,
        drive_resistant_allele_emergence_risk_pct=1.25,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 359 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_359_Verification"
    assert getattr(study, "target_population_suppression_pct") == 99.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Anopheles_gambiae_Doublesex_Homing_Gene_Drive_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Anopheles_gambiae_Doublesex_Homing_Gene_Drive_Model"

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
    assert fetched.name == "Study_359_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
