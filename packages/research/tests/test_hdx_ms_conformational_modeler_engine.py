"""Tests for Phase 380: Autonomous Proteome-Wide Hydrogen-Deuterium Exchange Mass Spectrometry (HDX-MS) Conformational State Modeler Engine."""

import pytest
from research.orchestration.hdx_ms_conformational_modeler_engine import HdxMsConformationalModelerEngine


def test_hdx_ms_conformational_modeler_engine():
    engine = HdxMsConformationalModelerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="hdx-ms-conformational-modeler",
        input_scale=1.0,
    )
    assert getattr(result, "hdx_peptic_peptide_sequence_coverage_pct") != 0
    assert getattr(result, "deuterium_incorporation_mass_accuracy_ppm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
