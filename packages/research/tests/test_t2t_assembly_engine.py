"""Tests for Phase 126 T2TStructuralVariantEngine."""

import pytest
from research.genomics.t2t_assembly_engine import T2TStructuralVariantEngine


def test_evaluate_assembly_metrics():
    engine = T2TStructuralVariantEngine()
    contigs = [150000000, 120000000, 100000000, 80000000]
    res = engine.evaluate_assembly_metrics(contigs, kmer_eval_qv=65.4)
    assert res["n50_bp"] >= 120000000
    assert res["l50"] <= 2
    assert res["qv_accuracy"] == 65.4
    assert res["error_rate_per_base"] < 1e-6


def test_call_structural_variants():
    engine = T2TStructuralVariantEngine()
    sv = engine.call_structural_variants("chr1", 145000000, 145045000, read_depth=50, split_reads_fraction=0.6)
    assert sv["chromosome"] == "chr1"
    assert sv["sv_length_bp"] == 45000
    assert sv["genotype_quality"] > 90.0
    assert sv["functional_impact_score"] > 0.5


def test_simulate_t2t_pipeline():
    engine = T2TStructuralVariantEngine()
    res = engine.simulate_t2t_pipeline(sample_name="HG002_T2T_Test")
    assert res["sample_name"] == "HG002_T2T_Test"
    assert res["telomere_telomere_closed_chromosomes"] == 24
    assert len(res["structural_variants"]) >= 4
    assert len(res["haplotype_blocks"]) >= 2
    assert res["summary"]["qv_score"] > 60.0
