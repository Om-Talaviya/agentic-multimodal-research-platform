"""Tests for Phase 309: Autonomous Single-Cell Multiome ATAC-Seq & RNA Co-Assay Cis-Regulatory Network Inference Engine Engine."""

import pytest
from research.orchestration.single_cell_multiome_cis_reg_network_engine import SingleCellMultiomeCisRegNetworkEngine


def test_single_cell_multiome_cis_reg_network_engine():
    engine = SingleCellMultiomeCisRegNetworkEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-multiome-cis-reg",
        input_scale=1.0,
    )
    assert getattr(result, "cis_regulatory_linkage_correlation_score") != 0
    assert getattr(result, "peak_to_gene_co_accessibility_r2") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
