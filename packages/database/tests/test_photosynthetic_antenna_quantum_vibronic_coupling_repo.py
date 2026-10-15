"""Tests for Phase 538: Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator Repo."""

import pytest
from database.repositories.photosynthetic_antenna_quantum_vibronic_coupling_repo import PhotosyntheticAntennaQuantumVibronicCouplingRepository


@pytest.mark.asyncio
async def test_photosynthetic_antenna_quantum_vibronic_coupling_repository(db_session):
    repo = PhotosyntheticAntennaQuantumVibronicCouplingRepository(db_session)

    study = await repo.create_study(
        name="Study_538_Verification",
        target_specimen="Light-Harvesting Complex II (LHCII) Trimer with 42 Chlorophyll Pigments embedded in Lipid Nanodisc",
        analytical_modality="quantum-vibronic-exciton-dynamics",
        excitonic_energy_transfer_efficiency_pct=98.6,
        quantum_coherence_dephasing_time_fs=420.0,
        vibronic_resonance_coupling_cm_inv=148.0,
        spectral_density_reorganization_energy_cm_inv=65.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 538 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_538_Verification"
    assert study.excitonic_energy_transfer_efficiency_pct == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Chlorophyll_a_b_Inter_Monomer_Coherent_Exciton_Path",
        profile_category="Primary Step",
        quantitative_value=98.6,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Chlorophyll_a_b_Inter_Monomer_Coherent_Exciton_Path"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="excitonic_energy_transfer_efficiency_pct",
        observed_value=98.6,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 98.6

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_538_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
