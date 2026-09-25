"""Tests for Phase 188: Spatial Metabolomics MALDI-MSI Tissue Architecture Engine Engine."""

import pytest
from research.metabolomics.spatial_maldi_metabolomics_engine import SpatialMaldiMetabolomicsEngine


def test_spatial_maldi_metabolomics_engine():
    engine = SpatialMaldiMetabolomicsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Spatial Metabolomics MALDI-MSI",
        input_scale=1.0,
    )
    assert getattr(result, "spatial_resolution_microns") > 0
    assert getattr(result, "metabolic_heterogeneity_index") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
