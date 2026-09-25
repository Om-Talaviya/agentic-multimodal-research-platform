"""Tests for Phase 179: circRNA Biogenesis Engine."""

import pytest
from research.genomics.circrna_biogenesis_engine import CircRNABiogenesisEngine


def test_circrna_biogenesis_simulation():
    engine = CircRNABiogenesisEngine()
    result = engine.simulate_circrna_biogenesis(
        host_gene_symbol="CDR1as",
        genomic_locus="chrX:139865339-139866824",
        exon_count=3,
        flanking_alu_elements_count=2,
        quaking_motif_present=True,
    )

    assert result.host_gene_symbol == "CDR1as"
    assert 0.0 <= result.backsplice_efficiency_score <= 1.0
    assert result.circular_form_half_life_hours > 24.0
    assert len(result.backsplice_junctions) == 3
    assert len(result.mirna_sponge_targets) > 0
    assert result.sponge_efficiency_index > 0.0
