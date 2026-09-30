"""Tests for Phase 405: Autonomous Ultra-High Plex CODEX Immune Neighborhood Spatial Interaction Network Repo."""

import pytest
from database.repositories.multiplexed_codex_neighborhood_repo import MultiplexedCodexNeighborhoodRepository


@pytest.mark.asyncio
async def test_multiplexed_codex_neighborhood_repository(db_session):
    repo = MultiplexedCodexNeighborhoodRepository(db_session)

    study = await repo.create_study(
        name="Study_405_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="multiplexed-codex-neighborhood",
        spatial_neighborhood_clustering_silhouette_score=0.88,
        cellular_contact_enrichment_z_score=4.65,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 405 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_405_Verification"
    assert getattr(study, "spatial_neighborhood_clustering_silhouette_score") == 0.88

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Tertiary_Lymphoid_Structure_TLS_CD20_CD3_CD8_Niche",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Tertiary_Lymphoid_Structure_TLS_CD20_CD3_CD8_Niche"

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
    assert fetched.name == "Study_405_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
