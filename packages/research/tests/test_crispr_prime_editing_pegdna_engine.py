"""Tests for Phase 180: CRISPR Prime Editing pegRNA Engine."""

import pytest
from research.genomics.crispr_prime_editing_pegdna_engine import CRISPRPrimeEditingPegDNAEngine


def test_crispr_prime_editing_pegdna_simulation():
    engine = CRISPRPrimeEditingPegDNAEngine()
    result = engine.simulate_pegdna_design(
        target_gene="HBB",
        intended_mutation_type="point_substitution",
        pbs_length_nt=13,
        rtt_length_nt=15,
        nick_to_edit_distance_bp=3,
        pe_system_version="PEmax_epegRNA",
    )

    assert result.target_gene == "HBB"
    assert 0.0 < result.predicted_prime_editing_efficiency <= 1.0
    assert result.indel_byproduct_frequency < 0.1
    assert len(result.pegdna_candidates) == 3
    assert len(result.flap_kinetics) == 6
    assert result.fidelity_index > 0.0
