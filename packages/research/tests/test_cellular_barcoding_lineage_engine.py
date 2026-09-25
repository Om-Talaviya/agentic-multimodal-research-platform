"""Tests for Phase 191: Cellular Barcoding & Lineage Tree Reconstructor Engine Engine."""

import pytest
from research.genomics.cellular_barcoding_lineage_engine import CellularBarcodingLineageEngine


def test_cellular_barcoding_lineage_engine():
    engine = CellularBarcodingLineageEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Cellular Barcoding Lineage",
        input_scale=1.0,
    )
    assert getattr(result, "lineage_tree_depth_generations") > 0
    assert getattr(result, "parsimony_reconstruction_accuracy") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
