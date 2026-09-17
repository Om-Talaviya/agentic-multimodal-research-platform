import pytest
from research.vaccine.neoepitope_engine import ProteogenomicNeoepitopeEngine

def test_neoepitope_engine_scoring_and_assembly():
    engine = ProteogenomicNeoepitopeEngine()

    # 1. Test MHC Affinity prediction
    affinity_strong = engine.predict_mhc_binding_affinity("KLVVVGADGV", "HLA-A*02:01")
    assert isinstance(affinity_strong, float)
    assert affinity_strong > 0.0

    # 2. Test Neoepitope Scoring
    scored = engine.score_neoepitope(
        mutated_gene="KRAS",
        peptide_mt="KLVVVGADGV",
        peptide_wt="KLVVVGAGGV",
        hla_allele="HLA-A*02:01",
        vaf_pct=38.5,
        expression_tpm=145.2,
    )
    assert scored["mutated_gene"] == "KRAS"
    assert "agretopicity_index" in scored
    assert "immunogenicity_rank_score" in scored
    assert 0.0 <= scored["immunogenicity_rank_score"] <= 1.0

    # 3. Test mRNA Polyepitope Assembly
    candidates = [
        scored,
        engine.score_neoepitope("TP53", "SQHMTEVVRQ", "SQHMTEVVRK", "HLA-A*02:01", 45.0, 90.0),
        engine.score_neoepitope("BRAF", "EDLTVKIGDF", "EDLTVKIGFL", "HLA-A*02:01", 52.0, 220.0),
    ]
    assembly = engine.assemble_mrna_polyepitope(candidates, top_k=2, linker="AAY")
    assert assembly["selected_neoepitope_count"] == 2
    assert "AAY" in assembly["polyepitope_peptide_sequence"]
    assert "MKWVTFISLLFLFSSAYS" in assembly["full_engineered_construct"]
    assert assembly["polyepitope_junction_cleavability_score"] >= 0.85
