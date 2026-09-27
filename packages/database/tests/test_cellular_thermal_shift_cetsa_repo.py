"""Tests for Phase 243: Autonomous Intact-Cell Cellular Thermal Shift Assay (CETSA) & Target Engagement Deconvolution Engine Repo."""

import pytest
from database.repositories.cellular_thermal_shift_cetsa_repo import CellularThermalShiftCetsaRepository


@pytest.mark.asyncio
async def test_cellular_thermal_shift_cetsa_repository(db_session):
    repo = CellularThermalShiftCetsaRepository(db_session)

    study = await repo.create_study(
        name="Study_243_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cellular-thermal-shift-cetsa",
        thermal_shift_delta_tm_celsius=7.8,
        target_engagement_apparent_ec50_nM=24.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 243 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_243_Verification"
    assert getattr(study, "thermal_shift_delta_tm_celsius") == 7.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CDK4_6_Inhibitor_Cellular_Thermal_Denaturation_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CDK4_6_Inhibitor_Cellular_Thermal_Denaturation_Map"

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
    assert fetched.name == "Study_243_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
