"""Tests for Phase 408: Autonomous Multi-State smFRET Hidden Markov Model Kinetic Rate Matrix Extractor Engine."""

import pytest
from research.orchestration.single_molecule_fret_kinetics_engine import SingleMoleculeFretKineticsEngine


def test_single_molecule_fret_kinetics_engine():
    engine = SingleMoleculeFretKineticsEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-molecule-fret-kinetics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "fret_efficiency_state_transition_rate_per_sec") > 0
    assert getattr(result, "viterbi_hidden_state_assignment_accuracy_pct") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 408" in result.summary_report
