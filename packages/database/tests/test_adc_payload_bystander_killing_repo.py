"""Tests for Phase 233: Autonomous Antibody-Drug Conjugate (ADC) Payload Bystander Killing & Lysosomal Cleavability Engine Repo."""

import pytest
from database.repositories.adc_payload_bystander_killing_repo import AdcPayloadBystanderKillingRepository


@pytest.mark.asyncio
async def test_adc_payload_bystander_killing_repository(db_session):
    repo = AdcPayloadBystanderKillingRepository(db_session)

    study = await repo.create_study(
        name="Study_233_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="adc-payload-bystander-killing",
        bystander_cytotoxicity_index=88.6,
        cleavage_rate_constant_kcat_over_km=1420.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 233 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_233_Verification"
    assert getattr(study, "bystander_cytotoxicity_index") == 88.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Trastuzumab_Deruxtecan_DXd_Bystander_Kinetics",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Trastuzumab_Deruxtecan_DXd_Bystander_Kinetics"

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
    assert fetched.name == "Study_233_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
