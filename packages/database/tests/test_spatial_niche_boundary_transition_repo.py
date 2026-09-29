"""Tests for Phase 268: Autonomous Spatial Transcriptomics De-Novo Niche Domain Boundary & Cell-Type Transition Graph Engine Repo."""

import pytest
from database.repositories.spatial_niche_boundary_transition_repo import SpatialNicheBoundaryTransitionRepository


@pytest.mark.asyncio
async def test_spatial_niche_boundary_transition_repository(db_session):
    repo = SpatialNicheBoundaryTransitionRepository(db_session)

    study = await repo.create_study(
        name="Study_268_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-niche-boundary-transition",
        spatial_boundary_gradient_sharpness_score=94.7,
        niche_transition_entropy=1.45,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 268 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_268_Verification"
    assert getattr(study, "spatial_boundary_gradient_sharpness_score") == 94.7

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Invasive_Tumor_Margin_Epithelial_Mesenchymal_Boundary",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Invasive_Tumor_Margin_Epithelial_Mesenchymal_Boundary"

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
    assert fetched.name == "Study_268_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
