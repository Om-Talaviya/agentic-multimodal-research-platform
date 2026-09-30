"""Tests for Phase 385: Autonomous Deep Generative Peptide-HLA-DP/DQ Class II Immunogenicity Predictor Engine."""

import pytest
from research.orchestration.peptide_hla_dp_dq_predictor_engine import PeptideHlaDpDqPredictorEngine


def test_peptide_hla_dp_dq_predictor_engine():
    engine = PeptideHlaDpDqPredictorEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="peptide-hla-dp-dq-predictor",
        input_scale=1.0,
    )
    assert getattr(result, "class2_pmhc_binding_affinity_auroc") != 0
    assert getattr(result, "core_register_alignment_accuracy_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
