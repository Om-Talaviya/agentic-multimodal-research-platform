"""
Tests for Phase 55: Computational Immunology Engine.
"""
from research.immunology.immunology_engine import ComputationalImmunologyEngine


def test_predict_pmhc_affinity():
    pred = ComputationalImmunologyEngine.predict_pMHC_affinity(
        peptide="EDLTVKIGD",
        hla_allele="HLA-A*02:01",
        mutation_variant="V600E",
        gene_symbol="BRAF",
    )
    assert "binding_ic50_nm" in pred
    assert "percentile_rank" in pred
    assert "composite_priority_score" in pred
    assert 0.0 <= pred["tcr_immunogenicity_score"] <= 1.0


def test_design_vaccine_construct():
    mock_epitopes = [
        {"peptide_sequence": "EDLTVKIGD", "composite_priority_score": 0.95},
        {"peptide_sequence": "ILDTAGKEEY", "composite_priority_score": 0.88},
    ]
    design = ComputationalImmunologyEngine.design_vaccine_construct(
        screen_id="test-screen-1",
        epitopes=mock_epitopes,
        construct_name="TestConstruct",
        linker="AAY",
    )
    assert design["full_polyepitope_sequence"] == "EDLTVKIGD-AAY-ILDTAGKEEY"
    assert len(design["ordered_epitopes"]) == 2
