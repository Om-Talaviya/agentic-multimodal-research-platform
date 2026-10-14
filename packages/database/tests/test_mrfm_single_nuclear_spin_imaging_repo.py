"""Tests for Phase 499: Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine Repo."""

import pytest
from database.repositories.mrfm_single_nuclear_spin_imaging_repo import MrfmSingleNuclearSpinImagingRepository


@pytest.mark.asyncio
async def test_mrfm_single_nuclear_spin_imaging_repository(db_session):
    repo = MrfmSingleNuclearSpinImagingRepository(db_session)

    study = await repo.create_study(
        name="Study_499_Verification",
        target_specimen="Ultra-Sensitive Silicon Nanocantilever with Ferromagnetic SmCo Tip over Vitrified Tobacco Mosaic Virus",
        analytical_modality="mrfm-single-spin-imaging",
        mrfm_spatial_resolution_nm=1.85,
        attonewton_force_gradient_sensitivity_aN_per_nm=4.2,
        spin_nutation_inversion_fidelity=0.985,
        three_d_spin_density_reconstruction_snr=19.4,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 499 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_499_Verification"
    assert study.mrfm_spatial_resolution_nm == 1.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="SmCo_Tip_Magnetic_Field_Gradient_Spin_Modulation",
        profile_category="Primary Step",
        quantitative_value=1.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "SmCo_Tip_Magnetic_Field_Gradient_Spin_Modulation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="mrfm_spatial_resolution_nm",
        observed_value=1.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_499_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
