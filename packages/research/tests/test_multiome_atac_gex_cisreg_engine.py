"""Tests for Phase 206: Single-Cell Multiome ATAC+GEX Peak-to-Gene Cis-Regulatory Engine Engine."""

import pytest
from research.genomics.multiome_atac_gex_cisreg_engine import MultiomeATACGEXCisRegEngine


def test_multiome_atac_gex_cisreg_engine():
    engine = MultiomeATACGEXCisRegEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Multiome ATAC GEX Cis-Reg",
        input_scale=1.0,
    )
    assert getattr(result, "peak_gene_correlation_pearson") != 0
    assert getattr(result, "transcription_factor_regulon_activity_auc") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
