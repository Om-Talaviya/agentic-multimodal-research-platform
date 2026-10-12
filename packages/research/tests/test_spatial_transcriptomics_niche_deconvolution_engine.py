"""Tests for Phase 431: Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine."""

import pytest
from research.orchestration.spatial_transcriptomics_niche_deconvolution_engine import SpatialTranscriptomicsNicheDeconvolutionEngine


def test_spatial_transcriptomics_niche_deconvolution_engine():
    engine = SpatialTranscriptomicsNicheDeconvolutionEngine()
    result = engine.analyze(
        target_specimen="10x Visium HD Formalin-Fixed Paraffin-Embedded Tissue Slice",
        analytical_modality="spatial-niche-deconvolution",
        input_scale=1.0,
    )

    assert result.target_specimen == "10x Visium HD Formalin-Fixed Paraffin-Embedded Tissue Slice"
    assert result.confidence_score >= 0.95
    assert result.sub_spot_cell_type_purity > 0.0
    assert result.niche_cross_talk_significance_p > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous High-Plex Spatial T" in result.summary_report
