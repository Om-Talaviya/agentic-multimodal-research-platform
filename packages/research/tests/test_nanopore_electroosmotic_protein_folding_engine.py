"""Tests for Phase 553: Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

import pytest
from research.orchestration.nanopore_electroosmotic_protein_folding_engine import NanoporeElectroosmoticProteinFoldingEngine


def test_nanopore_electroosmotic_protein_folding_engine():
    engine = NanoporeElectroosmoticProteinFoldingEngine()
    result = engine.analyze(
        target_specimen="Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias",
        analytical_modality="nanopore-electroosmotic-folding",
        input_scale=1.0,
    )

    assert result.target_specimen == "Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias"
    assert result.confidence_score >= 0.95
    assert result.single_molecule_trap_dwell_time_s != 0.0
    assert result.electroosmotic_holding_force_pn != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Nanopore Electro-Os" in result.summary_report
