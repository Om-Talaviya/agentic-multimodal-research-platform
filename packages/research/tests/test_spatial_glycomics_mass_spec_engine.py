"""Tests for Phase 240: Autonomous Spatial MALDI-MSI Glycan Branching & Sialylation Tissue Micro-Architecture Engine Engine."""

import pytest
from research.orchestration.spatial_glycomics_mass_spec_engine import SpatialGlycomicsMassSpecEngine


def test_spatial_glycomics_mass_spec_engine():
    engine = SpatialGlycomicsMassSpecEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-glycomics-mass-spec",
        input_scale=1.0,
    )
    assert getattr(result, "glycan_isomer_resolution_score") != 0
    assert getattr(result, "core_fucosylation_intensity_ratio") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
