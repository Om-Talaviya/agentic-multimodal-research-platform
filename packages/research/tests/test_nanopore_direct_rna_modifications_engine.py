"""Tests for Phase 257: Autonomous In-Silico Nanopore Direct RNA Sequencing (dRNA-seq) Base Modification Decoding Engine Engine."""

import pytest
from research.orchestration.nanopore_direct_rna_modifications_engine import NanoporeDirectRnaModificationsEngine


def test_nanopore_direct_rna_modifications_engine():
    engine = NanoporeDirectRnaModificationsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-direct-rna-modifications",
        input_scale=1.0,
    )
    assert getattr(result, "m6a_modification_detection_accuracy_pct") != 0
    assert getattr(result, "polya_tail_length_resolution_nt") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
