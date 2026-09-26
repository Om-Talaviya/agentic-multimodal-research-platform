"""Tests for Phase 203: Pan-Cancer Spatial Tumor Microenvironment Immune Infiltration Ranker Repo."""

import pytest
from database.repositories.spatial_tme_immune_infiltration_repo import SpatialTMEImmuneInfiltrationRepository


@pytest.mark.asyncio
async def test_spatial_tme_immune_infiltration_repository(db_session):
    repo = SpatialTMEImmuneInfiltrationRepository(db_session)

    study = await repo.create_study(
        name="Study_203_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Spatial TME Immune Infiltration",
        cd8_cytotoxic_infiltration_density=480.5,
        checkpoint_response_predictive_score=0.924,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 203 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_203_Verification"
    assert getattr(study, "cd8_cytotoxic_infiltration_density") == 480.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Tertiary Lymphoid Structure (TLS) Mature Node [CD20+ / CD3+ / CXCL13+]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Tertiary Lymphoid Structure (TLS) Mature Node [CD20+ / CD3+ / CXCL13+]"

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
    assert fetched.name == "Study_203_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
