"""Tests for Phase 129 PanDDACrystallographyEngine."""

import pytest
from research.structural.pandda_engine import PanDDACrystallographyEngine


def test_compute_statistical_ground_state():
    engine = PanDDACrystallographyEngine()
    densities = [1.0, 0.98, 1.02, 1.01, 0.99]
    res = engine.compute_statistical_ground_state(densities, dataset_count=120)
    assert res["mean_density"] == 1.0
    assert res["sigma"] < 0.1
    assert res["background_model_quality"] == "High-Fidelity"


def test_evaluate_pandda_event():
    engine = PanDDACrystallographyEngine()
    res = engine.evaluate_pandda_event(
        peak_z_score=6.8,
        observed_density=2.5,
        background_mean=1.0,
        background_sigma=0.08,
        heavy_atom_count=14,
        kd_micromolar=80.0,
    )
    assert res["z_peak_score"] == 6.8
    assert res["estimated_occupancy"] > 0.6
    assert res["ligand_efficiency_le"] > 0.35
    assert res["is_confident_hit"] is True


def test_simulate_fragment_screen():
    engine = PanDDACrystallographyEngine()
    res = engine.simulate_fragment_screen(
        campaign_name="Mpro_PanDDA_Campaign",
        target_protein="Main Protease",
        total_crystals=350,
    )
    assert res["campaign_name"] == "Mpro_PanDDA_Campaign"
    assert res["total_crystals_soaked"] == 350
    assert len(res["fragment_hits"]) >= 3
    assert res["summary"]["events_detected"] >= 3
    assert res["summary"]["mean_le"] > 0.3
