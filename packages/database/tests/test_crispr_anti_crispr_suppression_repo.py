"""Tests for Phase 237: Autonomous Anti-CRISPR (Acr) Protein Interaction & Gene Editing Precision Regulator Engine Repo."""

import pytest
from database.repositories.crispr_anti_crispr_suppression_repo import CrisprAntiCrisprSuppressionRepository


@pytest.mark.asyncio
async def test_crispr_anti_crispr_suppression_repository(db_session):
    repo = CrisprAntiCrisprSuppressionRepository(db_session)

    study = await repo.create_study(
        name="Study_237_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-anti-crispr-suppression",
        off_target_ablation_efficiency_pct=99.4,
        on_target_retention_ratio_pct=95.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 237 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_237_Verification"
    assert getattr(study, "off_target_ablation_efficiency_pct") == 99.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AcrIIA4_Timed_Off_Switch_Cas9_Ribonucleoprotein",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "AcrIIA4_Timed_Off_Switch_Cas9_Ribonucleoprotein"

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
    assert fetched.name == "Study_237_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
