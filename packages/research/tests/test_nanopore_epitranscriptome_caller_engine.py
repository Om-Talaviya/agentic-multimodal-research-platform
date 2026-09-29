"""Tests for Phase 336: Autonomous Direct-RNA Nanopore Sequencing Base Modification & m6A/Pseudouridine Epitrancriptome Caller Engine."""

import pytest
from research.orchestration.nanopore_epitranscriptome_caller_engine import NanoporeEpitranscriptomeCallerEngine


def test_nanopore_epitranscriptome_caller_engine():
    engine = NanoporeEpitranscriptomeCallerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-epitranscriptome",
        input_scale=1.0,
    )
    assert getattr(result, "modification_calling_accuracy_auroc") != 0
    assert getattr(result, "stoichiometric_quantification_precision_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
