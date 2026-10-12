"""Tests for Phase 440: Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine Repo."""

import pytest
from database.repositories.super_resolution_minflux_nanometer_tracking_repo import MinfluxNanometerTrackingRepository


@pytest.mark.asyncio
async def test_super_resolution_minflux_nanometer_tracking_repository(db_session):
    repo = MinfluxNanometerTrackingRepository(db_session)

    study = await repo.create_study(
        name="Study_440_Verification",
        target_specimen="Living Motor Protein Myosin V Moving Along Actin Filament with Cy5 Label",
        analytical_modality="minflux-tracking",
        spatial_localization_precision_angstrom=8.5,
        temporal_resolution_us=120.0,
        photon_budget_efficiency_ratio=0.942,
        step_size_hand_over_hand_nm=36.2,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 440 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_440_Verification"
    assert study.spatial_localization_precision_angstrom == 8.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="MINFLUX_Donut_Minimum_Excitation_Position",
        profile_category="Primary Step",
        quantitative_value=8.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "MINFLUX_Donut_Minimum_Excitation_Position"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="spatial_localization_precision_angstrom",
        observed_value=8.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 8.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_440_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
