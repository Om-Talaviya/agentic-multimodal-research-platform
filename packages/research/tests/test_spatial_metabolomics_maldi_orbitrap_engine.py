"""Tests for Phase 311: Autonomous High-Resolution Atmospheric-Pressure MALDI-Orbitrap Spatial Metabolomics Deep Matrix Resolver Engine."""

import pytest
from research.orchestration.spatial_metabolomics_maldi_orbitrap_engine import SpatialMetabolomicsMaldiOrbitrapEngine


def test_spatial_metabolomics_maldi_orbitrap_engine():
    engine = SpatialMetabolomicsMaldiOrbitrapEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-metabolomics-maldi",
        input_scale=1.0,
    )
    assert getattr(result, "spatial_metabolite_annotation_confidence_pct") != 0
    assert getattr(result, "pixel_resolving_power_fwhm_microns") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
