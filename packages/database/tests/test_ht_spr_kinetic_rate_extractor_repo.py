"""Tests for Phase 348: Autonomous High-Throughput Surface Plasmon Resonance (HT-SPR) Kinetic Binding Rate Constants Extractor Repo."""

import pytest
from database.repositories.ht_spr_kinetic_rate_extractor_repo import HtSprKineticRateExtractorRepository


@pytest.mark.asyncio
async def test_ht_spr_kinetic_rate_extractor_repository(db_session):
    repo = HtSprKineticRateExtractorRepository(db_session)

    study = await repo.create_study(
        name="Study_348_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="ht-spr-kinetics",
        kinetic_dissociation_constant_kd_picomolar=42.0,
        spr_sensorgram_global_fit_confidence_pct=99.15,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 348 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_348_Verification"
    assert getattr(study, "kinetic_dissociation_constant_kd_picomolar") == 42.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Bococizumab_PCSK9_High_Throughput_Sensorgram_Array",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Bococizumab_PCSK9_High_Throughput_Sensorgram_Array"

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
    assert fetched.name == "Study_348_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
