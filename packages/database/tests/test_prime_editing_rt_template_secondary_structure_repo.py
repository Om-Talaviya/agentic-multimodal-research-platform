"""Tests for Phase 241: Autonomous Prime Editing RT Template Secondary Structure & Extension Velocity Forecaster Engine Repo."""

import pytest
from database.repositories.prime_editing_rt_template_secondary_structure_repo import PrimeEditingRtTemplateSecondaryStructureRepository


@pytest.mark.asyncio
async def test_prime_editing_rt_template_secondary_structure_repository(db_session):
    repo = PrimeEditingRtTemplateSecondaryStructureRepository(db_session)

    study = await repo.create_study(
        name="Study_241_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="prime-editing-rt-template-secondary-structure",
        rt_extension_processivity_score=96.2,
        hairpin_destabilization_delta_g_kcal_mol=8.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 241 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_241_Verification"
    assert getattr(study, "rt_extension_processivity_score") == 96.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CFTR_DeltaF508_Prime_Editing_pegRNA_Construct",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CFTR_DeltaF508_Prime_Editing_pegRNA_Construct"

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
    assert fetched.name == "Study_241_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
