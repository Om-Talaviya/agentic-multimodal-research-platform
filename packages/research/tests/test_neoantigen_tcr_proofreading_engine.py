"""Tests for Phase 378: Autonomous Neoantigen T-Cell Receptor (TCR) Kinetic Proofreading & Clonal Expansion Forecaster Engine."""

import pytest
from research.orchestration.neoantigen_tcr_proofreading_engine import NeoantigenTcrProofreadingEngine


def test_neoantigen_tcr_proofreading_engine():
    engine = NeoantigenTcrProofreadingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="neoantigen-tcr-proofreading",
        input_scale=1.0,
    )
    assert getattr(result, "tcr_pmhc_catch_bond_lifetime_seconds") != 0
    assert getattr(result, "antigen_specific_cd8_tcell_expansion_fold") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
