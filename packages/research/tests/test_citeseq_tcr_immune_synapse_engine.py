"""Tests for Phase 420: Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver."""

import pytest
from research.orchestration.citeseq_tcr_immune_synapse_engine import CiteseqTcrImmuneSynapseEngine


def test_citeseq_tcr_immune_synapse_engine():
    engine = CiteseqTcrImmuneSynapseEngine()
    result = engine.analyze(
        target_specimen="Human CD8+ Tumor-Infiltrating Lymphocytes with pMHC Multimer",
        analytical_modality="citeseq-tcr-synapse",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human CD8+ Tumor-Infiltrating Lymphocytes with pMHC Multimer"
    assert result.confidence_score >= 0.95
    assert result.immune_synapse_contact_area_um2 > 0.0
    assert result.surface_protein_abundance_umi > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Cell Multi-M" in result.summary_report
