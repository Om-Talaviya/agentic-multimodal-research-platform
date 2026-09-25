"""Tests for Phase 188: Spatial Metabolomics MALDI-MSI Tissue Architecture Engine Repo."""

import pytest
from database.repositories.spatial_maldi_metabolomics_repo import SpatialMaldiMetabolomicsRepository


@pytest.mark.asyncio
async def test_spatial_maldi_metabolomics_repository(db_session):
    repo = SpatialMaldiMetabolomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_188_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Spatial Metabolomics MALDI-MSI",
        spatial_resolution_microns=20.0,
        metabolic_heterogeneity_index=0.874,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 188 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_188_Verification"
    assert getattr(study, "spatial_resolution_microns") == 20.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="2-Hydroxyglutarate (2-HG) [m/z 147.030]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "2-Hydroxyglutarate (2-HG) [m/z 147.030]"

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
    assert fetched.name == "Study_188_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
