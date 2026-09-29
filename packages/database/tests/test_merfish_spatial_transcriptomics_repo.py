"""Tests for Phase 332: Autonomous Multiplexed In Situ RNA Hybridization (MERFISH) 3D Subcellular Transcript Location Modeler Repo."""

import pytest
from database.repositories.merfish_spatial_transcriptomics_repo import MerfishSpatialTranscriptomicsRepository


@pytest.mark.asyncio
async def test_merfish_spatial_transcriptomics_repository(db_session):
    repo = MerfishSpatialTranscriptomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_332_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="merfish-spatial-transcriptomics",
        subcellular_transcript_detection_efficiency_pct=94.8,
        spatial_optical_barcode_false_positive_rate_pct=1.15,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 332 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_332_Verification"
    assert getattr(study, "subcellular_transcript_detection_efficiency_pct") == 94.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Human_Cerebral_Cortex_4000_Gene_Subcellular_Spatial_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Human_Cerebral_Cortex_4000_Gene_Subcellular_Spatial_Map"

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
    assert fetched.name == "Study_332_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
