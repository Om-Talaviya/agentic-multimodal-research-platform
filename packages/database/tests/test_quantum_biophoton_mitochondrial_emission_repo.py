"""Tests for Phase 509: Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster Repo."""

import pytest
from database.repositories.quantum_biophoton_mitochondrial_emission_repo import QuantumBiophotonMitochondrialEmissionRepository


@pytest.mark.asyncio
async def test_quantum_biophoton_mitochondrial_emission_repository(db_session):
    repo = QuantumBiophotonMitochondrialEmissionRepository(db_session)

    study = await repo.create_study(
        name="Study_509_Verification",
        target_specimen="Permeabilized Primary Cortical Neurons in Cryogenic Photomultiplier Chamber under Glutamate Stress",
        analytical_modality="ultra-weak-biophoton-chemiluminescence",
        ultra_weak_photon_count_cps_per_cm2=14.8,
        singlet_oxygen_decay_spectral_emission_nm=1270.0,
        lipid_peroxy_chemiluminescence_quantum_yield=8.5e-05,
        respiratory_chain_complex_leak_correlation=0.912,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 509 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_509_Verification"
    assert study.ultra_weak_photon_count_cps_per_cm2 == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Mitochondrial_Singlet_Oxygen_Radiative_Deactivation",
        profile_category="Primary Step",
        quantitative_value=14.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Mitochondrial_Singlet_Oxygen_Radiative_Deactivation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="ultra_weak_photon_count_cps_per_cm2",
        observed_value=14.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_509_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
