"""Tests for Phase 372: Autonomous Correlative Light and Electron Microscopy (CLEM) Subcellular 3D Super-Resolution Deconvolver Engine."""

import pytest
from research.orchestration.clem_subcellular_deconvolution_engine import ClemSubcellularDeconvolutionEngine


def test_clem_subcellular_deconvolution_engine():
    engine = ClemSubcellularDeconvolutionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="clem-subcellular-deconvolution",
        input_scale=1.0,
    )
    assert getattr(result, "correlative_fiducial_registration_accuracy_nm") != 0
    assert getattr(result, "subcellular_organelle_segmentation_dice_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
