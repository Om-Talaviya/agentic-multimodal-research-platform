"""Tests for Phase 409: Autonomous Targeted RNA Degradation (RIBOTAC) Small Molecule RNase L Recruiter Engine."""

import pytest
from research.orchestration.targeted_rna_degradation_ribotac_engine import TargetedRnaDegradationRibotacEngine


def test_targeted_rna_degradation_ribotac_engine():
    engine = TargetedRnaDegradationRibotacEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="targeted-rna-degradation-ribotac",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "target_rna_transcript_cleavage_efficiency_pct") > 0
    assert getattr(result, "rnase_l_dimerization_activation_selectivity_fold") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 409" in result.summary_report
