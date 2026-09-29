"""Tests for Phase 268: Autonomous Spatial Transcriptomics De-Novo Niche Domain Boundary & Cell-Type Transition Graph Engine Engine."""

import pytest
from research.orchestration.spatial_niche_boundary_transition_engine import SpatialNicheBoundaryTransitionEngine


def test_spatial_niche_boundary_transition_engine():
    engine = SpatialNicheBoundaryTransitionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-niche-boundary-transition",
        input_scale=1.0,
    )
    assert getattr(result, "spatial_boundary_gradient_sharpness_score") != 0
    assert getattr(result, "niche_transition_entropy") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
