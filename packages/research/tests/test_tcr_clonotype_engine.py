"""
Unit tests for Phase 104: TCR/BCR Clonotype & Immune Repertoire Engine.
"""
import pytest
from research.immunology.tcr_clonotype_engine import TCRClonotypeEngine

def test_tcr_diversity_metrics_calculation():
    engine = TCRClonotypeEngine()
    
    # Perfectly even distribution across 4 clones
    counts = [25, 25, 25, 25]
    metrics = engine.compute_diversity_metrics(counts)
    
    assert metrics["shannon_entropy"] > 0
    assert metrics["gini_simpson_index"] == pytest.approx(0.75, abs=0.01)
    assert metrics["clonality_score"] == pytest.approx(0.0, abs=0.01)

    # Monoclonal expansion
    mono_counts = [1000]
    mono_metrics = engine.compute_diversity_metrics(mono_counts)
    assert mono_metrics["shannon_entropy"] == 0.0
    assert mono_metrics["gini_simpson_index"] == 0.0
    assert mono_metrics["clonality_score"] == 1.0

def test_tcr_repertoire_analysis_workflow():
    engine = TCRClonotypeEngine()

    raw_clonotypes = [
        {"cdr3_aa": "CASSLAPGATNEKLFF", "v_gene": "TRBV7-2*01", "j_gene": "TRBJ1-4*01", "count": 600},
        {"cdr3_aa": "CASSLIGVSSYNEQFF", "v_gene": "TRBV19*01", "j_gene": "TRBJ2-1*01", "count": 400},
    ]

    analysis = engine.analyze_repertoire(
        sample_name="Test-PBMC",
        raw_clonotypes=raw_clonotypes,
        organism="Homo sapiens",
        chain_type="TCR_ALPHA_BETA"
    )

    assert analysis["sample_name"] == "Test-PBMC"
    assert analysis["total_cells"] == 1000
    assert analysis["clonotype_count"] == 2
    assert analysis["clonotypes"][0]["antigen_specificity"] == "EBV_BMLF1 (GLCTLVAML)"
    assert analysis["clonotypes"][1]["antigen_specificity"] == "CMV_pp65 (NLVPMVATV)"
    assert len(analysis["vdj_pairings"]) == 2
