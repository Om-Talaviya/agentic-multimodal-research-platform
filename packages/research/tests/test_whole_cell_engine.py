"""Tests for WholeCellMetabolicEngine."""
import pytest
from research.metabolism.whole_cell_engine import WholeCellMetabolicEngine


def test_whole_cell_engine_ecoli():
    engine = WholeCellMetabolicEngine()
    result = engine.run_dynamic_fba(
        model_id="iML1515",
        carbon_source="GLUCOSE",
        initial_glucose_g_L=20.0,
        initial_biomass_g_L=0.1,
        simulation_duration_hours=10.0,
        time_step_hours=2.0,
    )

    assert "model" in result
    assert result["model"]["organism_name"] == "Escherichia coli K-12 MG1655"
    assert result["model"]["total_reactions_count"] == 2712
    assert result["model"]["optimal_growth_rate_hr1"] > 0.8

    assert "flux_states" in result
    assert len(result["flux_states"]) >= 6
    subsystems = [f["subsystem"] for f in result["flux_states"]]
    assert "GLYCOLYSIS" in subsystems
    assert "TCA_CYCLE" in subsystems

    assert "simulation_traces" in result
    assert len(result["simulation_traces"]) == 6
    assert result["simulation_traces"][-1]["biomass_concentration_g_L"] > 0.1
    assert result["simulation_traces"][-1]["glucose_concentration_g_L"] < 20.0


def test_whole_cell_engine_yeast():
    engine = WholeCellMetabolicEngine()
    result = engine.run_dynamic_fba(
        model_id="iMM904",
        carbon_source="GLUCOSE",
    )

    assert result["model"]["organism_name"] == "Saccharomyces cerevisiae S288C"
    assert result["model"]["total_reactions_count"] == 1575
