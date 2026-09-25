"""Tests for Phase 189: Nanopore Direct RNA Sequencing & Epitranscriptomic Modification Mapper Engine."""

import pytest
from research.genomics.nanopore_direct_rna_engine import NanoporeDirectRNAEngine


def test_nanopore_direct_rna_engine():
    engine = NanoporeDirectRNAEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Nanopore Direct RNA Epitranscriptomics",
        input_scale=1.0,
    )
    assert getattr(result, "median_polya_tail_length_nt") > 0
    assert getattr(result, "epitranscriptomic_modification_stoichiometry") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
