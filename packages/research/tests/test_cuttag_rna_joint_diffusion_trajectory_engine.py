"""Tests for Phase 495: Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

import pytest
from research.orchestration.cuttag_rna_joint_diffusion_trajectory_engine import CuttagRnaJointDiffusionTrajectoryEngine


def test_cuttag_rna_joint_diffusion_trajectory_engine():
    engine = CuttagRnaJointDiffusionTrajectoryEngine()
    result = engine.analyze(
        target_specimen="Developing Murine Cortical Plate Radial Glia Lineage with H3K4me3 / H3K27ac and mRNA Co-Assay",
        analytical_modality="cuttag-rna-joint-diffusion",
        input_scale=1.0,
    )

    assert result.target_specimen == "Developing Murine Cortical Plate Radial Glia Lineage with H3K4me3 / H3K27ac and mRNA Co-Assay"
    assert result.confidence_score >= 0.95
    assert result.epigenomic_chromatin_velocity_coherence != 0.0
    assert result.promoter_enhancer_concordance_score != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Spatial Multi-Modal" in result.summary_report
