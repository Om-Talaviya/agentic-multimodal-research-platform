"""Tests for Phase 532: Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter Repo."""

import pytest
from database.repositories.single_cell_spatial_lipidomics_maldi_repo import SingleCellSpatialLipidomicsMaldiRepository


@pytest.mark.asyncio
async def test_single_cell_spatial_lipidomics_maldi_repository(db_session):
    repo = SingleCellSpatialLipidomicsMaldiRepository(db_session)

    study = await repo.create_study(
        name="Study_532_Verification",
        target_specimen="High-Precision Cryo-Sectioned Mouse Brain Cortical Layer with 5um Sub-Cellular Laser Spot",
        analytical_modality="single-cell-maldi-lipidomics",
        phospholipid_species_resolved_count=385.0,
        spatial_laser_ablation_pitch_um=5.0,
        mass_resolving_power_fwhm_at_m_z_800=140000.0,
        cell_type_lipidomic_silhouette_score=0.89,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 532 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_532_Verification"
    assert study.phospholipid_species_resolved_count == 385.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Phosphatidylcholine_Sphingomyelin_Membrane_Ratio_Map",
        profile_category="Primary Step",
        quantitative_value=385.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Phosphatidylcholine_Sphingomyelin_Membrane_Ratio_Map"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="phospholipid_species_resolved_count",
        observed_value=385.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 385.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_532_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
