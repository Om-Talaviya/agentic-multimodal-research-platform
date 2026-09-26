"""Tests for Phase 208: Long-Read Structural Variant & De Novo Assembly Engine Engine."""

import pytest
from research.genomics.long_read_sv_assembly_engine import LongReadSVAssemblyEngine


def test_long_read_sv_assembly_engine():
    engine = LongReadSVAssemblyEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Long-Read SV Assembly",
        input_scale=1.0,
    )
    assert getattr(result, "contig_n50_megabases") != 0
    assert getattr(result, "structural_variant_breakpoint_precision_bp") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
