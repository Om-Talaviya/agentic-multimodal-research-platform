"""Tests for Phase 197: Cryo-EM Focused Refinement & Deep Symmetrization Engine Engine."""

import pytest
from research.structural.cryoem_focused_refinement_engine import CryoEMFocusedRefinementEngine


def test_cryoem_focused_refinement_engine():
    engine = CryoEMFocusedRefinementEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Cryo-EM Focused Refinement",
        input_scale=1.0,
    )
    assert getattr(result, "local_resolution_angstroms") > 0
    assert getattr(result, "map_to_model_cross_correlation") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
