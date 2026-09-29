"""Tests for Phase 307: Autonomous Spatial Proteomics Imaging Mass Cytometry (IMC) Single-Cell Neighborhood Interaction & Escape Engine Engine."""

import pytest
from research.orchestration.imc_spatial_proteomics_neighborhood_engine import ImcSpatialProteomicsNeighborhoodEngine


def test_imc_spatial_proteomics_neighborhood_engine():
    engine = ImcSpatialProteomicsNeighborhoodEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="imc-spatial-proteomics-neighborhood",
        input_scale=1.0,
    )
    assert getattr(result, "cellular_neighborhood_classification_f1_score") != 0
    assert getattr(result, "tumor_immune_spatial_evasion_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
