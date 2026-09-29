"""Tests for Phase 311: Autonomous High-Resolution Atmospheric-Pressure MALDI-Orbitrap Spatial Metabolomics Deep Matrix Resolver Repo."""

import pytest
from database.repositories.spatial_metabolomics_maldi_orbitrap_repo import SpatialMetabolomicsMaldiOrbitrapRepository


@pytest.mark.asyncio
async def test_spatial_metabolomics_maldi_orbitrap_repository(db_session):
    repo = SpatialMetabolomicsMaldiOrbitrapRepository(db_session)

    study = await repo.create_study(
        name="Study_311_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-metabolomics-maldi",
        spatial_metabolite_annotation_confidence_pct=97.4,
        pixel_resolving_power_fwhm_microns=4.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 311 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_311_Verification"
    assert getattr(study, "spatial_metabolite_annotation_confidence_pct") == 97.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glioblastoma_Hypoxic_Core_Lipidomic_MALDI_Spatial_Grid",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Glioblastoma_Hypoxic_Core_Lipidomic_MALDI_Spatial_Grid"

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
    assert fetched.name == "Study_311_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
