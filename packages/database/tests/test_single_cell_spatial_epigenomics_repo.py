"""Tests for Phase 397: High-Plex Single-Cell Cut&Tag Spatial Epigenomic Chromatin Profiler Repo."""

import pytest
from database.repositories.single_cell_spatial_epigenomics_repo import SingleCellSpatialEpigenomicsRepository


@pytest.mark.asyncio
async def test_single_cell_spatial_epigenomics_repository(db_session):
    repo = SingleCellSpatialEpigenomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_397_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-spatial-epigenomics",
        chromatin_peak_signal_to_noise_enrichment=42.5,
        spatial_cellular_epigenome_resolution_um=8.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 397 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_397_Verification"
    assert getattr(study, "chromatin_peak_signal_to_noise_enrichment") == 42.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="H3K27ac_Super_Enhancer_Tissue_Domain_Spatial_Landscape",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "H3K27ac_Super_Enhancer_Tissue_Domain_Spatial_Landscape"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_397_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
