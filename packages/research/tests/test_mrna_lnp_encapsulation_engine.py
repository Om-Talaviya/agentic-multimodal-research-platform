"""Tests for Phase 201: Therapeutic mRNA LNP Encapsulation & Structure Thermodynamics Engine Engine."""

import pytest
from research.therapeutics.mrna_lnp_encapsulation_engine import MRNALNPEncapsulationEngine


def test_mrna_lnp_encapsulation_engine():
    engine = MRNALNPEncapsulationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mRNA LNP Encapsulation",
        input_scale=1.0,
    )
    assert getattr(result, "encapsulation_efficiency_percent") > 0
    assert getattr(result, "polydispersity_index_pdi") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
