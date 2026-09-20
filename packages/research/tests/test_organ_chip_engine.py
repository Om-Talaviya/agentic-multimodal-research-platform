"""
Unit tests for Phase 108: Organ-on-a-Chip Fluidic Dynamics Engine.
"""
import pytest
from research.biophysics.organ_chip_engine import MicrofluidicBiochipEngine

def test_fluidic_parameters_calculation():
    engine = MicrofluidicBiochipEngine()
    
    # Standard microfluidic perfusion (30 uL/min, 500x150 um channel)
    params = engine.compute_fluidic_parameters(
        flow_rate_ul_min=30.0,
        width_um=500.0,
        height_um=150.0,
        viscosity_cp=1.0
    )

    assert params["flow_velocity_mm_s"] > 0.0
    assert params["reynolds_number"] < 10.0  # Microfluidic laminar regime (Re << 2000)
    assert params["shear_stress_dyn_cm2"] > 0.0

def test_organ_chip_simulation():
    engine = MicrofluidicBiochipEngine()
    
    sim = engine.simulate_organ_chip(
        chip_name="BBB-Test-Chip",
        organ_type="BLOOD_BRAIN_BARRIER",
        flow_rate_ul_min=30.0
    )

    assert sim["chip_name"] == "BBB-Test-Chip"
    assert len(sim["channels"]) == 2
    assert sim["endothelial_barrier_integrity_teer"] >= 1000.0
    assert len(sim["shear_profiles"]) == 5
    assert sim["shear_profiles"][0]["tight_junction_expression"] > 80.0
