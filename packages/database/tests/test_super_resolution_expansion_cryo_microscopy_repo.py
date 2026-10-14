"""Tests for Phase 522: Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler Repo."""

import pytest
from database.repositories.super_resolution_expansion_cryo_microscopy_repo import SuperResolutionExpansionCryoMicroscopyRepository


@pytest.mark.asyncio
async def test_super_resolution_expansion_cryo_microscopy_repository(db_session):
    repo = SuperResolutionExpansionCryoMicroscopyRepository(db_session)

    study = await repo.create_study(
        name="Study_522_Verification",
        target_specimen="4x Polyacrylate Hydrogel Swollen Vitrified Mouse Hippocampal Synapse with Pre- and Post-Synaptic Markers",
        analytical_modality="cryo-expansion-super-resolution",
        effective_isotropic_optical_resolution_nm=14.5,
        macromolecular_isotropy_expansion_factor=4.15,
        fluorescent_label_retention_efficiency_pct=92.0,
        clem_spatial_registration_fiducial_error_nm=8.5,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 522 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_522_Verification"
    assert study.effective_isotropic_optical_resolution_nm == 14.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Dendritic_Spine_Postsynaptic_Density_Nanocluster_Map",
        profile_category="Primary Step",
        quantitative_value=14.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Dendritic_Spine_Postsynaptic_Density_Nanocluster_Map"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="effective_isotropic_optical_resolution_nm",
        observed_value=14.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_522_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
