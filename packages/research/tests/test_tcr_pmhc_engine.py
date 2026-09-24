"""Tests for TCRpMHCAffinityEngine."""

from research.immunology.tcr_pmhc_engine import (
    TCRpMHCAffinityEngine,
    TCRpMHCPredictionRequest,
)


def test_tcr_pmhc_engine():
    engine = TCRpMHCAffinityEngine()
    req = TCRpMHCPredictionRequest(
        tcr_name="MAGE-A4-TCR",
        cdr3_alpha_seq="CAVSETGGSYIPTF",
        cdr3_beta_seq="CASSLGQAYEQYF",
        target_peptide="GVYDGREHTV",
        hla_allele="HLA-A*02:01",
    )
    res = engine.predict(req)
    assert res.status == "COMPLETED"
    assert res.binding_kd_um > 0
    assert len(res.cross_reactivity_scan) == 3
