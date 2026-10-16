"""Tests for Phase 548: Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine."""

import pytest
from research.orchestration.cryo_electron_ptychography_reconstruction_engine import CryoElectronPtychographyReconstructionEngine


def test_cryo_electron_ptychography_reconstruction_engine():
    engine = CryoElectronPtychographyReconstructionEngine()
    result = engine.analyze(
        target_specimen="Intact Vitrified Chlamydomonas reinhardtii Chloroplast Membrane Thylakoid with Fast Direct Electron Camera 4D-STEM",
        analytical_modality="cryo-ptychography-4d-stem",
        input_scale=1.0,
    )

    assert result.target_specimen == "Intact Vitrified Chlamydomonas reinhardtii Chloroplast Membrane Thylakoid with Fast Direct Electron Camera 4D-STEM"
    assert result.confidence_score >= 0.95
    assert result.sub_angstrom_phase_contrast_resolution_a != 0.0
    assert result.inelastic_mean_free_path_depth_nm != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Cell Cryo-Electr" in result.summary_report
