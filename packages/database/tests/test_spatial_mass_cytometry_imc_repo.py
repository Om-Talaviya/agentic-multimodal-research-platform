"""Tests for Phase 221: Autonomous Spatial Imaging Mass Cytometry (IMC) 40-Plex Phenotyping & Microenvironment Niche Ranker Engine Repo."""

import pytest
from database.repositories.spatial_mass_cytometry_imc_repo import SpatialMassCytometryImcRepository


@pytest.mark.asyncio
async def test_spatial_mass_cytometry_imc_repository(db_session):
    repo = SpatialMassCytometryImcRepository(db_session)

    study = await repo.create_study(
        name="Study_221_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-mass-cytometry-imc",
        segmentation_f1_score=0.948,
        phenotypic_purity_pct=98.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 221 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_221_Verification"
    assert getattr(study, "segmentation_f1_score") == 0.948

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="IMC_40Plex_Melanoma_Stroma_Margin_ROI01",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "IMC_40Plex_Melanoma_Stroma_Margin_ROI01"

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
    assert fetched.name == "Study_221_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
