"""Tests for Phase 428: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

import pytest
from research.orchestration.liquid_cell_tem_nucleation_engine import LiquidCellTemNucleationEngine


def test_liquid_cell_tem_nucleation_engine():
    engine = LiquidCellTemNucleationEngine()
    result = engine.analyze(
        target_specimen="Silicon Nitride Liquid Cell with Gold Nanocrystal Growth Solution",
        analytical_modality="liquid-cell-tem",
        input_scale=1.0,
    )

    assert result.target_specimen == "Silicon Nitride Liquid Cell with Gold Nanocrystal Growth Solution"
    assert result.confidence_score >= 0.95
    assert result.nucleation_rate_particles_per_s_um2 > 0.0
    assert result.critical_nucleus_radius_nm > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Situ Liquid-Cell" in result.summary_report
