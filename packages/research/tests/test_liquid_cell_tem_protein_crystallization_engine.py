"""Tests for Phase 520: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

import pytest
from research.orchestration.liquid_cell_tem_protein_crystallization_engine import LiquidCellTemProteinCrystallizationEngine


def test_liquid_cell_tem_protein_crystallization_engine():
    engine = LiquidCellTemProteinCrystallizationEngine()
    result = engine.analyze(
        target_specimen="Silicon Nitride Microchip Graphene Liquid Cell with Supersaturated Hen Egg-White Lysozyme Solution",
        analytical_modality="liquid-cell-tem-crystallization",
        input_scale=1.0,
    )

    assert result.target_specimen == "Silicon Nitride Microchip Graphene Liquid Cell with Supersaturated Hen Egg-White Lysozyme Solution"
    assert result.confidence_score >= 0.95
    assert result.critical_nucleus_radius_nm != 0.0
    assert result.non_classical_pre_nucleation_cluster_density_per_um3 != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Situ Liquid-Cell" in result.summary_report
