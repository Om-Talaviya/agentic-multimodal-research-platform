"""
Unit tests for Phase 109: CyTOF Research Engine.
"""
import pytest
import math
from research.cytometry.cytof_engine import CyTOFPhenotyperEngine

def test_arcsinh_transformation():
    engine = CyTOFPhenotyperEngine()
    
    # Check arcsinh transform
    val = engine.arcsinh_transform(raw_value=450.0, cofactor=5.0)
    expected = math.asinh(450.0 / 5.0)
    assert abs(val - expected) < 1e-4
    assert val > 5.0

def test_cytof_panel_simulation():
    engine = CyTOFPhenotyperEngine()
    
    result = engine.simulate_cytof_panel(
        experiment_name="Simulation-PBMC",
        tissue_type="PBMC",
        cell_count=10000,
        cofactor=5.0
    )

    assert result["experiment_name"] == "Simulation-PBMC"
    assert len(result["channels"]) >= 15
    assert len(result["clusters"]) >= 8
    assert result["summary"]["dominant_phenotype"] is not None
    assert result["summary"]["t_cell_compartment_pct"] > 50.0
