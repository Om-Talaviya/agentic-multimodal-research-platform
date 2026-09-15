"""Tests for CRISPRGuideDesignEngine."""

import pytest
from research.crispr_engine import CRISPRGuideDesignEngine


def test_crispr_engine_design_guides():
    engine = CRISPRGuideDesignEngine()

    target_seq = "ATGGGCACCGTCAGCTCCAGGCGGTCCTGGTGGCCGCTGCCACTGCTGCTGCTGCTGCTGCTGCTCCTGGGTCCCGCGGGCGCCCGTGCGCAGGAGGACGAGGACGGCGACTACGAGGAGCTGGTGCTAGCCTTGCGTTCCGAGGAGGACGGCCTGGCCGAAGCACCCGAGCACGGAACCACAGCCACCTTCCACCGCTGCGCCAAGGATCCGTGGCGGTTGCCCGGCACCTAC"

    result = engine.design_guides(
        target_gene="PCSK9",
        target_sequence=target_seq,
        cas_enzyme="SpCas9",
        organism="Homo sapiens",
        max_guides=5,
    )

    assert result.target_gene == "PCSK9"
    assert result.cas_enzyme == "SpCas9"
    assert result.pam_motif == "NGG"
    assert len(result.guide_rnas) > 0
    assert len(result.guide_rnas) <= 5

    # Check first guide properties
    g = result.guide_rnas[0]
    assert len(g.spacer_sequence_20nt) == 20
    assert len(g.pam_sequence) == 3
    assert g.strand in ["+", "-"]
    assert 0.0 <= g.gc_content_pct <= 100.0
    assert 0.0 <= g.on_target_efficiency_score <= 100.0
    assert 0.0 <= g.off_target_cfd_score <= 100.0
    assert g.recommendation_tier in ["optimal", "moderate", "low"]
    assert g.oligo_forward_top.startswith("5'-CACC")
    assert g.oligo_reverse_bottom.startswith("5'-AAAC")

    # Check off targets
    assert len(g.off_target_sites) >= 1
    assert g.off_target_sites[0].mismatch_count >= 1

    # Check base editing profiles
    assert len(g.base_editing_profiles) >= 1
    assert g.base_editing_profiles[0].editing_window_start == 4
    assert g.base_editing_profiles[0].editing_window_end == 8
