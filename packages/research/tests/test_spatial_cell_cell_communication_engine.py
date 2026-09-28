"""Tests for Phase 247: Autonomous Spatial Transcriptomics Cell-Cell Communication & Distance-Decay Ligand-Receptor Engine Engine."""

import pytest
from research.orchestration.spatial_cell_cell_communication_engine import SpatialCellCellCommunicationEngine


def test_spatial_cell_cell_communication_engine():
    engine = SpatialCellCellCommunicationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-cell-cell-communication",
        input_scale=1.0,
    )
    assert getattr(result, "spatial_interaction_potential_score") != 0
    assert getattr(result, "distance_decay_effective_radius_um") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
