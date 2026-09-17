"""Tests for LNP Formulation Simulator Engine."""
import pytest
from research.lnp.lnp_engine import LNPFormulationSimulatorEngine


def test_lnp_simulation_default():
    engine = LNPFormulationSimulatorEngine()
    result = engine.simulate_formulation({
        "formulation_name": "mRNA Lipid Nanoparticle System",
        "cargo_type": "mRNA",
        "ionizable_lipid_name": "ALC-0315",
        "np_ratio": 6.0,
        "flow_rate_ratio_aqueous_organic": 3.0,
        "total_flow_rate_ml_min": 12.0,
    })

    assert result["formulation_name"] == "mRNA Lipid Nanoparticle System"
    assert result["cargo_type"] == "mRNA"
    assert result["mean_diameter_nm"] > 50.0
    assert result["encapsulation_efficiency_pct"] > 80.0
    assert result["apparent_pka"] >= 6.2 and result["apparent_pka"] <= 6.8
    assert len(result["components"]) == 4
    assert result["membrane_profile"]["endosomal_escape_efficiency_pct"] > 10.0


def test_lnp_simulation_custom_components():
    engine = LNPFormulationSimulatorEngine()
    custom_components = [
        {
            "component_name": "SM-102",
            "lipid_category": "IONIZABLE_LIPID",
            "molar_percentage": 50.0,
            "molecular_weight_g_mol": 710.0,
            "charge_at_ph7": 0.05,
        },
        {
            "component_name": "PEG-DMG",
            "lipid_category": "PEG_LIPID",
            "molar_percentage": 2.5,
            "molecular_weight_g_mol": 2500.0,
            "charge_at_ph7": 0.0,
        },
    ]

    result = engine.simulate_formulation(
        formulation_input={"formulation_name": "High-PEG Construct", "np_ratio": 8.0},
        raw_components=custom_components,
    )

    assert result["formulation_name"] == "High-PEG Construct"
    assert len(result["components"]) == 2
    assert result["mean_diameter_nm"] < 100.0
