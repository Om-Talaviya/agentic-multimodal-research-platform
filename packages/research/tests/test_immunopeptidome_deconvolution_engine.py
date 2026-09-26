"""Tests for Phase 213: Autonomous Mass Spectrometry Immunopeptidomics & Non-Canonical Cryptic Peptide Deconvolution Engine Engine."""

import pytest
from research.orchestration.immunopeptidome_deconvolution_engine import ImmunopeptidomeDeconvolutionEngine


def test_immunopeptidome_deconvolution_engine():
    engine = ImmunopeptidomeDeconvolutionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="immunopeptidome-deconvolution",
        input_scale=1.0,
    )
    assert getattr(result, "spectral_identification_fdr_pct") != 0
    assert getattr(result, "presentation_affinity_nM") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
