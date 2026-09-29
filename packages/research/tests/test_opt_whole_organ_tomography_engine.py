"""Tests for Phase 367: Autonomous High-Resolution Optical Projection Tomography (OPT) Whole-Organ Cleared Tissue Reconstructor Engine."""

import pytest
from research.orchestration.opt_whole_organ_tomography_engine import OptWholeOrganTomographyEngine


def test_opt_whole_organ_tomography_engine():
    engine = OptWholeOrganTomographyEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="opt-whole-organ-tomography",
        input_scale=1.0,
    )
    assert getattr(result, "isotropic_spatial_voxel_resolution_microns") != 0
    assert getattr(result, "volumetric_reconstruction_ssim_index") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
