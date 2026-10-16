"""Tests for Phase 563: Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter."""

import pytest
from research.orchestration.whole_brain_connectomics_synapse_segmenter_engine import WholeBrainConnectomicsSynapseSegmenterEngine


def test_whole_brain_connectomics_synapse_segmenter_engine():
    engine = WholeBrainConnectomicsSynapseSegmenterEngine()
    result = engine.analyze(
        target_specimen="Serial Section Electron Tomography (FIB-SEM) of Adult Drosophila Melanogaster Central Brain at 4x4x4 nm3 Voxel Resolution",
        analytical_modality="whole-brain-connectomics-segmentation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Serial Section Electron Tomography (FIB-SEM) of Adult Drosophila Melanogaster Central Brain at 4x4x4 nm3 Voxel Resolution"
    assert result.confidence_score >= 0.95
    assert result.synaptic_junction_detection_f1_score != 0.0
    assert result.t_bar_active_zone_reconstruction_precision != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Whole-Brain Nanosca" in result.summary_report
