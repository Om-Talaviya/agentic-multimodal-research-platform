"""Tests for Phase 532: Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

import pytest
from research.orchestration.single_cell_spatial_lipidomics_maldi_engine import SingleCellSpatialLipidomicsMaldiEngine


def test_single_cell_spatial_lipidomics_maldi_engine():
    engine = SingleCellSpatialLipidomicsMaldiEngine()
    result = engine.analyze(
        target_specimen="High-Precision Cryo-Sectioned Mouse Brain Cortical Layer with 5um Sub-Cellular Laser Spot",
        analytical_modality="single-cell-maldi-lipidomics",
        input_scale=1.0,
    )

    assert result.target_specimen == "High-Precision Cryo-Sectioned Mouse Brain Cortical Layer with 5um Sub-Cellular Laser Spot"
    assert result.confidence_score >= 0.95
    assert result.phospholipid_species_resolved_count != 0.0
    assert result.spatial_laser_ablation_pitch_um != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous High-Mass-Resolutio" in result.summary_report
