"""Tests for Phase 281: Autonomous In-Silico Antibody-Drug Conjugate (ADC) Bystander Killing & Payload Diffusion Dynamics Forecaster Repo."""

import pytest
from database.repositories.adc_bystander_killing_diffusion_repo import AdcBystanderKillingDiffusionRepository


@pytest.mark.asyncio
async def test_adc_bystander_killing_diffusion_repository(db_session):
    repo = AdcBystanderKillingDiffusionRepository(db_session)

    study = await repo.create_study(
        name="Study_281_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="adc-bystander-killing-diffusion",
        bystander_cytotoxicity_radius_um=65.4,
        cleavable_linker_stability_half_life_days=9.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 281 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_281_Verification"
    assert getattr(study, "bystander_cytotoxicity_radius_um") == 65.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Trastuzumab_Deruxtecan_Bystander_Diffusion_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Trastuzumab_Deruxtecan_Bystander_Diffusion_Model"

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
    assert fetched.name == "Study_281_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
