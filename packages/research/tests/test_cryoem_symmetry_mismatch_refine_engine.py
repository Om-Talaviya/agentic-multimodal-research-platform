"""Tests for Phase 235: Autonomous Cryo-EM Symmetry-Mismatch & Helical Filament Reconstruction Engine Engine."""

import pytest
from research.orchestration.cryoem_symmetry_mismatch_refine_engine import CryoEMSymmetryMismatchRefineEngine


def test_cryoem_symmetry_mismatch_refine_engine():
    engine = CryoEMSymmetryMismatchRefineEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-symmetry-mismatch-refine",
        input_scale=1.0,
    )
    assert getattr(result, "helical_pitch_rise_angstrom") != 0
    assert getattr(result, "symmetry_deconvolution_fsc_angstrom") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
