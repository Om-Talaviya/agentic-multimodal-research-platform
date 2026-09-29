"""Tests for Phase 301: Autonomous Single-Cell Lineage Tracing Multi-Locus CRISPR Barcode Scar Deconvolution & Phylogeny Reconstructor Engine."""

import pytest
from research.orchestration.crispr_lineage_barcode_phylogeny_engine import CrisprLineageBarcodePhylogenyEngine


def test_crispr_lineage_barcode_phylogeny_engine():
    engine = CrisprLineageBarcodePhylogenyEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-lineage-barcode-phylogeny",
        input_scale=1.0,
    )
    assert getattr(result, "tree_reconstruction_parsimony_score") != 0
    assert getattr(result, "lineage_commitment_branching_depth") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
