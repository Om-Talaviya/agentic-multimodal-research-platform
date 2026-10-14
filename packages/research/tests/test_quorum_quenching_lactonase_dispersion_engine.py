"""Tests for Phase 485: Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

import pytest
from research.orchestration.quorum_quenching_lactonase_dispersion_engine import QuorumQuenchingLactonaseDispersionEngine


def test_quorum_quenching_lactonase_dispersion_engine():
    engine = QuorumQuenchingLactonaseDispersionEngine()
    result = engine.analyze(
        target_specimen="Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)",
        analytical_modality="quorum-quenching-lactonase",
        input_scale=1.0,
    )

    assert result.target_specimen == "Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)"
    assert result.confidence_score >= 0.95
    assert result.ahl_hydrolysis_kcat_over_km_M_inv_s_inv != 0.0
    assert result.biofilm_extracellular_matrix_reduction_pct != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Bacterial Quorum Qu" in result.summary_report
