"""Tests for Phase 565: Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer Repo."""

import pytest
from database.repositories.quantum_entangled_photon_multiphoton_imaging_repo import QuantumEntangledPhotonMultiphotonImagingRepository


@pytest.mark.asyncio
async def test_quantum_entangled_photon_multiphoton_imaging_repository(db_session):
    repo = QuantumEntangledPhotonMultiphotonImagingRepository(db_session)

    study = await repo.create_study(
        name="Study_565_Verification",
        target_specimen="Intact Vitrified Mouse Cortical Brain Slices illuminated with Polarization-Entangled Photon Pairs at 800nm",
        analytical_modality="entangled-photon-multiphoton",
        two_photon_absorption_cross_section_enhancement_fold=185.0,
        imaging_tissue_penetration_depth_um=950.0,
        photobleaching_rate_suppression_pct=88.5,
        quantum_sub_shot_noise_snr_gain_db=5.4,
        confidence_score=0.998,
        status="completed",
        summary_report="Phase 565 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_565_Verification"
    assert study.two_photon_absorption_cross_section_enhancement_fold == 185.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Entangled_Photon_Deep_Layer_Dendritic_Spine_Point",
        profile_category="Primary Step",
        quantitative_value=185.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Entangled_Photon_Deep_Layer_Dendritic_Spine_Point"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="two_photon_absorption_cross_section_enhancement_fold",
        observed_value=185.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 185.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_565_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
