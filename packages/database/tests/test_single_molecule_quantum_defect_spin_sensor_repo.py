"""Tests for Phase 540: Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor Repo."""

import pytest
from database.repositories.single_molecule_quantum_defect_spin_sensor_repo import SingleMoleculeQuantumDefectSpinSensorRepository


@pytest.mark.asyncio
async def test_single_molecule_quantum_defect_spin_sensor_repository(db_session):
    repo = SingleMoleculeQuantumDefectSpinSensorRepository(db_session)

    study = await repo.create_study(
        name="Study_540_Verification",
        target_specimen="Fluorescent Nanodiamond with Single NV- Spin Defect internalized in Living Single Macrophage Cell",
        analytical_modality="nv-center-quantum-sensing",
        magnetic_field_sensitivity_nT_sqrt_hz=12.4,
        intracellular_thermal_sensitivity_mK_sqrt_hz=45.0,
        spin_coherence_time_t2_us=185.0,
        odmr_spectral_contrast_pct=14.8,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 540 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_540_Verification"
    assert study.magnetic_field_sensitivity_nT_sqrt_hz == 12.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="NV_Minus_Zero_Field_Splitting_Resonance_Dip",
        profile_category="Primary Step",
        quantitative_value=12.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "NV_Minus_Zero_Field_Splitting_Resonance_Dip"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="magnetic_field_sensitivity_nT_sqrt_hz",
        observed_value=12.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 12.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_540_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
