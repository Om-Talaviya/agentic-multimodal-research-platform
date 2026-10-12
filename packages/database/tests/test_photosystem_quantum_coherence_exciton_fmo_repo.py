"""Tests for Phase 441: Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler Repo."""

import pytest
from database.repositories.photosystem_quantum_coherence_exciton_fmo_repo import PhotosystemQuantumCoherenceRepository


@pytest.mark.asyncio
async def test_photosystem_quantum_coherence_exciton_fmo_repository(db_session):
    repo = PhotosystemQuantumCoherenceRepository(db_session)

    study = await repo.create_study(
        name="Study_441_Verification",
        target_specimen="Green Sulfur Bacteria Chlorobium tepidum FMO Bacteriochlorophyll Trimer",
        analytical_modality="quantum-exciton-fmo",
        exciton_transfer_efficiency_ratio=0.991,
        quantum_coherence_lifetime_fs=420.0,
        site_energy_disorder_cm_inv=85.0,
        sink_bchl_trapping_rate_ps_inv=1.85,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 441 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_441_Verification"
    assert study.exciton_transfer_efficiency_ratio == 0.991

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Bacteriochlorophyll_Site_Hamiltonian_Matrix",
        profile_category="Primary Step",
        quantitative_value=0.991,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Bacteriochlorophyll_Site_Hamiltonian_Matrix"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="exciton_transfer_efficiency_ratio",
        observed_value=0.991,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.991

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_441_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
