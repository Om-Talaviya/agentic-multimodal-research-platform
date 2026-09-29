"""Tests for Phase 334: Autonomous Single-Cell Proteomic Thermal Shift Assay (PISA) Drug-Target Engagement Decoupler Repo."""

import pytest
from database.repositories.pisa_thermal_shift_assay_repo import PisaThermalShiftAssayRepository


@pytest.mark.asyncio
async def test_pisa_thermal_shift_assay_repository(db_session):
    repo = PisaThermalShiftAssayRepository(db_session)

    study = await repo.create_study(
        name="Study_334_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="pisa-thermal-shift",
        thermal_melting_point_shift_delta_tm_celsius=6.8,
        target_engagement_apparent_kd_nm=24.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 334 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_334_Verification"
    assert getattr(study, "thermal_melting_point_shift_delta_tm_celsius") == 6.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Kinome_Pan_Inhibitor_Thermal_Shift_Profile_10000_Proteins",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Kinome_Pan_Inhibitor_Thermal_Shift_Profile_10000_Proteins"

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
    assert fetched.name == "Study_334_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
