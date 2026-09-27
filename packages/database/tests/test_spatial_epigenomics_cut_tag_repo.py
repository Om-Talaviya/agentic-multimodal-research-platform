"""Tests for Phase 229: Autonomous Spatial Epigenomic Cleavage Under Targets and Tagmentation (CUT&Tag) Chromatin Landscape Engine Repo."""

import pytest
from database.repositories.spatial_epigenomics_cut_tag_repo import SpatialEpigenomicsCutTagRepository


@pytest.mark.asyncio
async def test_spatial_epigenomics_cut_tag_repository(db_session):
    repo = SpatialEpigenomicsCutTagRepository(db_session)

    study = await repo.create_study(
        name="Study_229_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-epigenomics-cut-tag",
        signal_to_noise_frip_score=0.88,
        spatial_epigenomic_resolution_um=20.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 229 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_229_Verification"
    assert getattr(study, "signal_to_noise_frip_score") == 0.88

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Spatial_CUTandTag_Embryonic_Brain_H3K27ac",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Spatial_CUTandTag_Embryonic_Brain_H3K27ac"

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
    assert fetched.name == "Study_229_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
