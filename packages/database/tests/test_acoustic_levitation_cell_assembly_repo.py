"""Tests for Phase 412: Autonomous Acoustic Levitation 3D Scaffold-Free Spheroid Assembly Dynamics Engine Repo."""

import pytest
from database.repositories.acoustic_levitation_cell_assembly_repo import AcousticLevitationCellAssemblyRepository


@pytest.mark.asyncio
async def test_acoustic_levitation_cell_assembly_repository(db_session):
    repo = AcousticLevitationCellAssemblyRepository(db_session)

    study = await repo.create_study(
        name="Study_412_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="acoustic-levitation-cell-assembly",
        spheroid_sphericity_index_geometric_uniformity=0.962,
        acoustic_radiation_pressure_nodal_aggregation_time_sec=42.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 412 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_412_Verification"
    assert getattr(study, "spheroid_sphericity_index_geometric_uniformity") == 0.962

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ultrasonic_Standing_Wave_2MHz_Pressure_Node_Array",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ultrasonic_Standing_Wave_2MHz_Pressure_Node_Array"

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
    assert fetched.name == "Study_412_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
