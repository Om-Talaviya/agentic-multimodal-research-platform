"""Tests for Phase 234: Autonomous Single-Cell & Spatial Alternative Splicing Isoform Deconvolution Engine Engine."""

import pytest
from research.orchestration.single_cell_spatial_splice_junction_engine import SingleCellSpatialSpliceJunctionEngine


def test_single_cell_spatial_splice_junction_engine():
    engine = SingleCellSpatialSpliceJunctionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-spatial-splice-junction",
        input_scale=1.0,
    )
    assert getattr(result, "psi_quantification_accuracy_pct") != 0
    assert getattr(result, "isoform_switching_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
