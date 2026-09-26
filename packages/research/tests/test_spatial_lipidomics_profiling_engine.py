"""Tests for Phase 199: Spatial Lipidomics & Membrane Biogenesis Deconvolution Engine Engine."""

import pytest
from research.metabolomics.spatial_lipidomics_profiling_engine import SpatialLipidomicsProfilingEngine


def test_spatial_lipidomics_profiling_engine():
    engine = SpatialLipidomicsProfilingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Spatial Lipidomics Profiling",
        input_scale=1.0,
    )
    assert getattr(result, "membrane_fluidity_saturation_ratio") > 0
    assert getattr(result, "ferroptosis_lipid_peroxidation_score") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
