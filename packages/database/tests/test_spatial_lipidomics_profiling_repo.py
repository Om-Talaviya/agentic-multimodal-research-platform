"""Tests for Phase 199: Spatial Lipidomics & Membrane Biogenesis Deconvolution Engine Repo."""

import pytest
from database.repositories.spatial_lipidomics_profiling_repo import SpatialLipidomicsProfilingRepository


@pytest.mark.asyncio
async def test_spatial_lipidomics_profiling_repository(db_session):
    repo = SpatialLipidomicsProfilingRepository(db_session)

    study = await repo.create_study(
        name="Study_199_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Spatial Lipidomics Profiling",
        membrane_fluidity_saturation_ratio=1.48,
        ferroptosis_lipid_peroxidation_score=0.912,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 199 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_199_Verification"
    assert getattr(study, "membrane_fluidity_saturation_ratio") == 1.48

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Polyunsaturated Phosphatidylethanolamine [PE(18:0/20:4)]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Polyunsaturated Phosphatidylethanolamine [PE(18:0/20:4)]"

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
    assert fetched.name == "Study_199_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
