"""Tests for Phase 383: Autonomous In Vivo Viral Vector Tropism De-Targeting & Liver-Sparing Engineered Capsid Selector Repo."""

import pytest
from database.repositories.viral_tropism_detargeting_repo import ViralTropismDetargetingRepository


@pytest.mark.asyncio
async def test_viral_tropism_detargeting_repository(db_session):
    repo = ViralTropismDetargetingRepository(db_session)

    study = await repo.create_study(
        name="Study_383_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="viral-tropism-detargeting",
        hepatic_sequestration_reduction_ratio_fold=45.0,
        target_tissue_cns_transduction_enrichment_fold=68.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 383 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_383_Verification"
    assert getattr(study, "hepatic_sequestration_reduction_ratio_fold") == 45.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AAV_PHP_eB_Engineered_Neurotropic_Capsid_Variant",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "AAV_PHP_eB_Engineered_Neurotropic_Capsid_Variant"

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
    assert fetched.name == "Study_383_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
