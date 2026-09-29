"""Tests for Phase 362: Autonomous In Situ Spatial ATAC-seq Nuclear Transcription Factor Regulon Binding Footprinter Repo."""

import pytest
from database.repositories.spatial_atac_regulon_footprint_repo import SpatialAtacRegulonFootprintRepository


@pytest.mark.asyncio
async def test_spatial_atac_regulon_footprint_repository(db_session):
    repo = SpatialAtacRegulonFootprintRepository(db_session)

    study = await repo.create_study(
        name="Study_362_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-atac-regulon-footprint",
        transcription_factor_footprint_flanking_depth_ratio=3.85,
        spatial_regulon_tissue_mapping_concordance_pct=97.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 362 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_362_Verification"
    assert getattr(study, "transcription_factor_footprint_flanking_depth_ratio") == 3.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Developing_Mouse_Embryo_Spatial_ATAC_Regulon_Landscape",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Developing_Mouse_Embryo_Spatial_ATAC_Regulon_Landscape"

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
    assert fetched.name == "Study_362_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
