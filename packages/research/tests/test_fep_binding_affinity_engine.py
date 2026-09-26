"""Tests for Phase 204: Molecular Dynamics Free Energy Perturbation (FEP) Binding Engine Engine."""

import pytest
from research.structural.fep_binding_affinity_engine import FEPBindingAffinityEngine


def test_fep_binding_affinity_engine():
    engine = FEPBindingAffinityEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="MD Free Energy Perturbation FEP",
        input_scale=1.0,
    )
    assert getattr(result, "relative_binding_free_energy_ddg") != 0
    assert getattr(result, "thermodynamic_cycle_hysteresis_error") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
