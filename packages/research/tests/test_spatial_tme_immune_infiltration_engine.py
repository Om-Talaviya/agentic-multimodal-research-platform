"""Tests for Phase 203: Pan-Cancer Spatial Tumor Microenvironment Immune Infiltration Ranker Engine."""

import pytest
from research.immunology.spatial_tme_immune_infiltration_engine import SpatialTMEImmuneInfiltrationEngine


def test_spatial_tme_immune_infiltration_engine():
    engine = SpatialTMEImmuneInfiltrationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Spatial TME Immune Infiltration",
        input_scale=1.0,
    )
    assert getattr(result, "cd8_cytotoxic_infiltration_density") > 0
    assert getattr(result, "checkpoint_response_predictive_score") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
