"""Tests for Phase 405: Autonomous Ultra-High Plex CODEX Immune Neighborhood Spatial Interaction Network Engine."""

import pytest
from research.orchestration.multiplexed_codex_neighborhood_engine import MultiplexedCodexNeighborhoodEngine


def test_multiplexed_codex_neighborhood_engine():
    engine = MultiplexedCodexNeighborhoodEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="multiplexed-codex-neighborhood",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "spatial_neighborhood_clustering_silhouette_score") > 0
    assert getattr(result, "cellular_contact_enrichment_z_score") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 405" in result.summary_report
