"""Tests for Phase 215: Autonomous Subcellular Spatial Transcriptomics Cell-Type Deconvolution & Niche Cell-Cell Communication Engine Engine."""

import pytest
from research.orchestration.spatial_transcriptomics_celltype_engine import SpatialTranscriptomicsCelltypeEngine


def test_spatial_transcriptomics_celltype_engine():
    engine = SpatialTranscriptomicsCelltypeEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-transcriptomics-celltype",
        input_scale=1.0,
    )
    assert getattr(result, "celltype_deconvolution_accuracy_pct") != 0
    assert getattr(result, "niche_colocalization_index") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
