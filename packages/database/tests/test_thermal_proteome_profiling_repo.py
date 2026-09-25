"""Tests for Phase 190: Thermal Proteome Profiling & Target Engagement Deconvolution Engine Repo."""

import pytest
from database.repositories.thermal_proteome_profiling_repo import ThermalProteomeProfilingRepository


@pytest.mark.asyncio
async def test_thermal_proteome_profiling_repository(db_session):
    repo = ThermalProteomeProfilingRepository(db_session)

    study = await repo.create_study(
        name="Study_190_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Thermal Proteome Profiling TPP",
        melting_temperature_shift_celsius=4.82,
        target_engagement_confidence_auc=0.968,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 190 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_190_Verification"
    assert getattr(study, "melting_temperature_shift_celsius") == 4.82

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Target Kinase CDK4 [ΔTm = +4.82°C]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Target Kinase CDK4 [ΔTm = +4.82°C]"

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
    assert fetched.name == "Study_190_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
