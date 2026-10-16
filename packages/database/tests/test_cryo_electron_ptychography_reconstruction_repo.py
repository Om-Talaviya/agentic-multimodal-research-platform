"""Tests for Phase 548: Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine Repo."""

import pytest
from database.repositories.cryo_electron_ptychography_reconstruction_repo import CryoElectronPtychographyReconstructionRepository


@pytest.mark.asyncio
async def test_cryo_electron_ptychography_reconstruction_repository(db_session):
    repo = CryoElectronPtychographyReconstructionRepository(db_session)

    study = await repo.create_study(
        name="Study_548_Verification",
        target_specimen="Intact Vitrified Chlamydomonas reinhardtii Chloroplast Membrane Thylakoid with Fast Direct Electron Camera 4D-STEM",
        analytical_modality="cryo-ptychography-4d-stem",
        sub_angstrom_phase_contrast_resolution_a=1.82,
        inelastic_mean_free_path_depth_nm=240.0,
        dose_efficiency_snr_gain_factor=5.8,
        phase_plate_wavefront_aberration_mrad=0.45,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 548 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_548_Verification"
    assert study.sub_angstrom_phase_contrast_resolution_a == 1.82

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Thylakoid_Photosystem_II_Dimer_Ptychographic_Phase_Patch",
        profile_category="Primary Step",
        quantitative_value=1.82,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Thylakoid_Photosystem_II_Dimer_Ptychographic_Phase_Patch"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="sub_angstrom_phase_contrast_resolution_a",
        observed_value=1.82,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.82

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_548_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
