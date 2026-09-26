"""Tests for Phase 215: Autonomous Subcellular Spatial Transcriptomics Cell-Type Deconvolution & Niche Cell-Cell Communication Engine Repo."""

import pytest
from database.repositories.spatial_transcriptomics_celltype_repo import SpatialTranscriptomicsCelltypeRepository


@pytest.mark.asyncio
async def test_spatial_transcriptomics_celltype_repository(db_session):
    repo = SpatialTranscriptomicsCelltypeRepository(db_session)

    study = await repo.create_study(
        name="Study_215_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-transcriptomics-celltype",
        celltype_deconvolution_accuracy_pct=97.3,
        niche_colocalization_index=0.88,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 215 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_215_Verification"
    assert getattr(study, "celltype_deconvolution_accuracy_pct") == 97.3

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="VisiumHD_BreastCancer_InvasiveMargin_Spot101",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "VisiumHD_BreastCancer_InvasiveMargin_Spot101"

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
    assert fetched.name == "Study_215_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
