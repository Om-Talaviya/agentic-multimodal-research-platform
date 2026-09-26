"""Tests for Phase 216: Autonomous Targeted Covalent Inhibitor (TCI) Electrophilic Warhead Reactivity & Cysteine Residence Time Engine Engine."""

import pytest
from research.orchestration.targeted_covalent_inhibitor_warhead_engine import TargetedCovalentInhibitorWarheadEngine


def test_targeted_covalent_inhibitor_warhead_engine():
    engine = TargetedCovalentInhibitorWarheadEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="targeted-covalent-inhibitor-warhead",
        input_scale=1.0,
    )
    assert getattr(result, "kinact_over_ki_M_s") != 0
    assert getattr(result, "cysteine_residence_time_hours") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
