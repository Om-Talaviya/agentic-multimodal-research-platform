"""Tests for Phase 407: Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker Engine."""

import pytest
from research.orchestration.antibody_humanness_immunogenicity_engine import AntibodyHumannessImmunogenicityEngine


def test_antibody_humanness_immunogenicity_engine():
    engine = AntibodyHumannessImmunogenicityEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="antibody-humanness-immunogenicity",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "antibody_humanness_t20_score_percentile") > 0
    assert getattr(result, "mhc_class_ii_immunogenic_epitope_risk_reduction_pct") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 407" in result.summary_report
