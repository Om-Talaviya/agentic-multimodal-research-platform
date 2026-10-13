"""Tests for Phase 470: Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine Repo."""

import pytest
from database.repositories.piezoelectric_collagen_matrix_transduction_repo import PiezoelectricCollagenMatrixTransductionRepository


@pytest.mark.asyncio
async def test_piezoelectric_collagen_matrix_transduction_repository(db_session):
    repo = PiezoelectricCollagenMatrixTransductionRepository(db_session)

    study = await repo.create_study(
        name="Study_470_Verification",
        target_specimen="Dense Fibrillar Type-I Collagen Fascicle Scaffold with Applied High-Frequency Axial Dynamic Strain",
        analytical_modality="piezoelectric-collagen-transduction",
        piezoelectric_coefficient_d33_pC_per_N=8.45,
        surface_potential_streaming_voltage_mV=42.0,
        dynamic_electromechanical_coupling_factor=0.285,
        osteogenic_mineralization_acceleration_index=2.65,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 470 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_470_Verification"
    assert study.piezoelectric_coefficient_d33_pC_per_N == 8.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Quasi_Hexagonal_Collagen_Fibril_Dipole_Orientation",
        profile_category="Primary Step",
        quantitative_value=8.45,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Quasi_Hexagonal_Collagen_Fibril_Dipole_Orientation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="piezoelectric_coefficient_d33_pC_per_N",
        observed_value=8.45,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 8.45

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_470_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
