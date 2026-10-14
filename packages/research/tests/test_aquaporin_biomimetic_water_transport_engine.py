"""Tests for Phase 491: Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

import pytest
from research.orchestration.aquaporin_biomimetic_water_transport_engine import AquaporinBiomimeticWaterTransportEngine


def test_aquaporin_biomimetic_water_transport_engine():
    engine = AquaporinBiomimeticWaterTransportEngine()
    result = engine.analyze(
        target_specimen="Polymer-Inorganic Biomimetic Aquaporin-Z Nanocomposite Membrane with Forward Osmosis Crossflow",
        analytical_modality="aquaporin-biomimetic-transport",
        input_scale=1.0,
    )

    assert result.target_specimen == "Polymer-Inorganic Biomimetic Aquaporin-Z Nanocomposite Membrane with Forward Osmosis Crossflow"
    assert result.confidence_score >= 0.95
    assert result.water_permeability_flux_lmh_bar != 0.0
    assert result.nacl_solute_rejection_percentage != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Biomimetic Syntheti" in result.summary_report
