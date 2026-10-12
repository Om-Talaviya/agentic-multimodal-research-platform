"""Tests for Phase 415: Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

import pytest
from research.orchestration.direct_rna_nanopore_pseudouridine_engine import DirectRnaNanoporePseudouridineEngine


def test_direct_rna_nanopore_pseudouridine_engine():
    engine = DirectRnaNanoporePseudouridineEngine()
    result = engine.analyze(
        target_specimen="Cellular Poly(A)+ Native mRNA Transcriptome",
        analytical_modality="direct-rna-nanopore",
        input_scale=1.0,
    )

    assert result.target_specimen == "Cellular Poly(A)+ Native mRNA Transcriptome"
    assert result.confidence_score >= 0.95
    assert result.pseudouridine_stoichiometry_ratio > 0.0
    assert result.nanopore_dwell_time_shift_ms > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Epitranscriptomic D" in result.summary_report
