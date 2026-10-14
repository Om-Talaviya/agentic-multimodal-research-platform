"""Tests for Phase 499: Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

import pytest
from research.orchestration.mrfm_single_nuclear_spin_imaging_engine import MrfmSingleNuclearSpinImagingEngine


def test_mrfm_single_nuclear_spin_imaging_engine():
    engine = MrfmSingleNuclearSpinImagingEngine()
    result = engine.analyze(
        target_specimen="Ultra-Sensitive Silicon Nanocantilever with Ferromagnetic SmCo Tip over Vitrified Tobacco Mosaic Virus",
        analytical_modality="mrfm-single-spin-imaging",
        input_scale=1.0,
    )

    assert result.target_specimen == "Ultra-Sensitive Silicon Nanocantilever with Ferromagnetic SmCo Tip over Vitrified Tobacco Mosaic Virus"
    assert result.confidence_score >= 0.95
    assert result.mrfm_spatial_resolution_nm != 0.0
    assert result.attonewton_force_gradient_sensitivity_aN_per_nm != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Molecule Mag" in result.summary_report
