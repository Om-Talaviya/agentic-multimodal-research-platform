"""Tests for Phase 128 CITEseqMultiModalEngine."""

import pytest
from research.singlecell.citeseq_engine import CITEseqMultiModalEngine


def test_dsb_normalization():
    engine = CITEseqMultiModalEngine()
    raw = [100.0, 200.0, 500.0]
    bg = [1.0, 2.0, 1.5, 0.8]
    dsb = engine.compute_dsb_normalization(raw, bg)
    assert len(dsb) == 3
    assert dsb[2] > dsb[1] > dsb[0]
    assert dsb[0] > 0


def test_wnn_fusion_weights():
    engine = CITEseqMultiModalEngine()
    weights = engine.compute_wnn_fusion_weights(0.40, 0.60)
    assert weights["weight_protein_adt"] == 0.6
    assert weights["weight_rna"] == 0.4


def test_simulate_citeseq_pipeline():
    engine = CITEseqMultiModalEngine()
    res = engine.simulate_citeseq_pipeline(sample_name="Colorectal_Cancer_TILs")
    assert res["sample_name"] == "Colorectal_Cancer_TILs"
    assert res["total_cells"] == 14500
    assert len(res["tags"]) >= 4
    assert len(res["concordance_profiles"]) >= 6
    assert res["summary"]["mean_protein_snr"] > 10.0
