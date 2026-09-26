"""Tests for Phase 211: Autonomous Single-Cell Copy Number Variation (scCNV) & Chromosomal Aneuploidy Karyotyper Engine Engine."""

import pytest
from research.orchestration.scrna_copy_number_karyotype_engine import ScRNACopyNumberKaryotypeEngine


def test_scrna_copy_number_karyotype_engine():
    engine = ScRNACopyNumberKaryotypeEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="scrna-copy-number-karyotype",
        input_scale=1.0,
    )
    assert getattr(result, "aneuploidy_confidence_score") != 0
    assert getattr(result, "breakpoint_resolution_kb") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
