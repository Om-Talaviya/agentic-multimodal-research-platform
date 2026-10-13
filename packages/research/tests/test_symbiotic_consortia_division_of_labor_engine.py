"""Tests for Phase 464: Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

import pytest
from research.orchestration.symbiotic_consortia_division_of_labor_engine import SymbioticConsortiaDivisionOfLaborEngine


def test_symbiotic_consortia_division_of_labor_engine():
    engine = SymbioticConsortiaDivisionOfLaborEngine()
    result = engine.analyze(
        target_specimen="Engineered E. coli and S. cerevisiae Cross-Feeding Co-Culture in Chemostat Bioreactor",
        analytical_modality="symbiotic-metabolic-labor-dynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Engineered E. coli and S. cerevisiae Cross-Feeding Co-Culture in Chemostat Bioreactor"
    assert result.confidence_score >= 0.95
    assert result.chemostat_steady_state_biomass_ratio != 0.0
    assert result.cross_feeding_metabolite_exchange_flux_mmol_g_hr != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Symbiotic" in result.summary_report
