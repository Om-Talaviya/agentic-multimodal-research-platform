"""Tests for Phase 514: Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

import pytest
from research.orchestration.deep_learning_tcr_pmhc_docking_energy_engine import DeepLearningTcrPmhcDockingEnergyEngine


def test_deep_learning_tcr_pmhc_docking_energy_engine():
    engine = DeepLearningTcrPmhcDockingEnergyEngine()
    result = engine.analyze(
        target_specimen="Structure-Resolved Complex of Human CD8+ TCR with Cancer-Testis Neoantigen NY-ESO-1 HLA-A*02:01",
        analytical_modality="egnn-tcr-pmhc-docking",
        input_scale=1.0,
    )

    assert result.target_specimen == "Structure-Resolved Complex of Human CD8+ TCR with Cancer-Testis Neoantigen NY-ESO-1 HLA-A*02:01"
    assert result.confidence_score >= 0.95
    assert result.predicted_binding_free_energy_delta_G_kcal_mol != 0.0
    assert result.cdr3_loop_interface_contact_rmsd_angstrom != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Equivariant Graph N" in result.summary_report
