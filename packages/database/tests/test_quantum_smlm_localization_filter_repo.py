"""Tests for Phase 547: Autonomous Quantum Super-Resolution Single-Molecule Localization Microscopy (SMLM) Quantum State Squeezing Filter Repo."""

import pytest
from database.repositories.quantum_smlm_localization_filter_repo import QuantumSmlmLocalizationFilterRepository


@pytest.mark.asyncio
async def test_quantum_smlm_localization_filter_repository(db_session):
    repo = QuantumSmlmLocalizationFilterRepository(db_session)

    study = await repo.create_study(
        name="Study_547_Verification",
        target_specimen="Single AlexaFluor-647 Fluorophores in Sub-Diffraction Nanoscale DNA Origami Grid with Squeezed Vacuum State Illumination",
        analytical_modality="quantum-smlm-squeezing",
        photon_localization_precision_nm=1.15,
        quantum_squeezing_shot_noise_reduction_db=4.2,
        point_spread_function_fisher_information=820.0,
        emitter_density_resolvable_per_um2=185.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 547 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_547_Verification"
    assert study.photon_localization_precision_nm == 1.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sub_Diffraction_Squeezed_Photon_Centroid_Cluster",
        profile_category="Primary Step",
        quantitative_value=1.15,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Sub_Diffraction_Squeezed_Photon_Centroid_Cluster"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="photon_localization_precision_nm",
        observed_value=1.15,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.15

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_547_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
