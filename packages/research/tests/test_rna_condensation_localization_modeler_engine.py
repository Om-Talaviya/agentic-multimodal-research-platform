"""Tests for Phase 321: Autonomous Intracellular RNA Zipcode Localization & Liquid-Liquid Phase Separation Condensate Modeler Engine."""

import pytest
from research.orchestration.rna_condensation_localization_modeler_engine import RnaCondensationLocalizationModelerEngine


def test_rna_condensation_localization_modeler_engine():
    engine = RnaCondensationLocalizationModelerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="rna-condensation-localization",
        input_scale=1.0,
    )
    assert getattr(result, "condensate_partition_coefficient_k") != 0
    assert getattr(result, "motor_protein_binding_affinity_kd_nm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
