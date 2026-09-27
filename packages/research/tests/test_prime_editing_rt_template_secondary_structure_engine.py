"""Tests for Phase 241: Autonomous Prime Editing RT Template Secondary Structure & Extension Velocity Forecaster Engine Engine."""

import pytest
from research.orchestration.prime_editing_rt_template_secondary_structure_engine import PrimeEditingRtTemplateSecondaryStructureEngine


def test_prime_editing_rt_template_secondary_structure_engine():
    engine = PrimeEditingRtTemplateSecondaryStructureEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="prime-editing-rt-template-secondary-structure",
        input_scale=1.0,
    )
    assert getattr(result, "rt_extension_processivity_score") != 0
    assert getattr(result, "hairpin_destabilization_delta_g_kcal_mol") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
