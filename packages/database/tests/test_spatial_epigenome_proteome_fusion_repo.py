"""Tests for Phase 375: Autonomous Deep In Situ Spatial Epigenome-Proteome Co-Assay Tensor Fusion Matrix Repo."""

import pytest
from database.repositories.spatial_epigenome_proteome_fusion_repo import SpatialEpigenomeProteomeFusionRepository


@pytest.mark.asyncio
async def test_spatial_epigenome_proteome_fusion_repository(db_session):
    repo = SpatialEpigenomeProteomeFusionRepository(db_session)

    study = await repo.create_study(
        name="Study_375_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-epigenome-proteome-fusion",
        joint_tensor_reconstruction_explained_variance_pct=96.8,
        cross_modality_mutual_information_score=0.915,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 375 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_375_Verification"
    assert getattr(study, "joint_tensor_reconstruction_explained_variance_pct") == 96.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glioblastoma_Tumor_Margin_Joint_Epigenome_Proteome_Atlas",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Glioblastoma_Tumor_Margin_Joint_Epigenome_Proteome_Atlas"

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
    assert fetched.name == "Study_375_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
