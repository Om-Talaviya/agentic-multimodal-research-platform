import pytest
from research.stability.stability_engine import BiotherapeuticStabilityEngine

def test_biotherapeutic_stability_engine():
    engine = BiotherapeuticStabilityEngine()

    hc_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS"
    lc_seq = "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"

    # 1. Test SAP Score and Thermal metrics
    res = engine.compute_spatial_aggregation_propensity(hc_seq, lc_seq)
    assert 0.0 <= res["aggregation_propensity_score"] <= 1.0
    assert 60.0 <= res["melting_temp_tm1_celsius"] <= 85.0
    assert res["shelf_life_months_at_4c"] > 12.0
    assert isinstance(res["hydrophobic_patches"], list)

    # 2. Test Formulation Excipient Screen
    form = engine.optimize_formulation_buffer(
        sap_score=res["aggregation_propensity_score"],
        buffer_type="Histidine",
        ph=6.0,
        surfactant="Polysorbate 80",
        tonicity_agent="Sucrose",
    )
    assert form["monomer_retention_pct_at_40c"] >= 90.0
    assert form["formulation_stability_grade"] in ["STABLE", "MARGINAL"]
