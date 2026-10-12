"""Tests for Phase 422: Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

import pytest
from research.orchestration.ligand_residence_time_koff_engine import LigandResidenceTimeKoffEngine


def test_ligand_residence_time_koff_engine():
    engine = LigandResidenceTimeKoffEngine()
    result = engine.analyze(
        target_specimen="Kinase Allosteric Pocket with Type II Small Molecule Inhibitor",
        analytical_modality="residence-time-koff",
        input_scale=1.0,
    )

    assert result.target_specimen == "Kinase Allosteric Pocket with Type II Small Molecule Inhibitor"
    assert result.confidence_score >= 0.95
    assert result.unbinding_rate_koff_s_inv > 0.0
    assert result.residence_time_minutes > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Allosteric Ligand R" in result.summary_report
