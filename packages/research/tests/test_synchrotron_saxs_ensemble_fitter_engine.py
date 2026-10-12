"""Tests for Phase 433: Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

import pytest
from research.orchestration.synchrotron_saxs_ensemble_fitter_engine import SynchrotronSaxsEnsembleFitterEngine


def test_synchrotron_saxs_ensemble_fitter_engine():
    engine = SynchrotronSaxsEnsembleFitterEngine()
    result = engine.analyze(
        target_specimen="Intrinsically Disordered Kinase Domain in Solution",
        analytical_modality="synchrotron-saxs",
        input_scale=1.0,
    )

    assert result.target_specimen == "Intrinsically Disordered Kinase Domain in Solution"
    assert result.confidence_score >= 0.95
    assert result.radius_of_gyration_Rg_angstrom > 0.0
    assert result.kratky_plot_flexibility_index > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synchrotron Small-A" in result.summary_report
