"""Tests for Phase 360: Autonomous Proteome-Wide Native Mass Spectrometry (Native MS) Non-Covalent Complex Stoichiometry Resolver Engine."""

import pytest
from research.orchestration.native_ms_complex_stoichiometry_engine import NativeMsComplexStoichiometryEngine


def test_native_ms_complex_stoichiometry_engine():
    engine = NativeMsComplexStoichiometryEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="native-ms-complex-stoichiometry",
        input_scale=1.0,
    )
    assert getattr(result, "quaternary_mass_determination_accuracy_ppm") != 0
    assert getattr(result, "charge_state_deconvolution_confidence_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
