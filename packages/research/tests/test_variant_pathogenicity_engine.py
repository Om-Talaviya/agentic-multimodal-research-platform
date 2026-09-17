"""Tests for Variant Pathogenicity Engine."""
import pytest
from research.genomics.variant_pathogenicity_engine import VariantPathogenicityEngine


def test_evaluate_pathogenic_null_variant():
    engine = VariantPathogenicityEngine()
    variant = {
        "gene_symbol": "BRCA1",
        "hgvs_c": "c.5266dupC",
        "hgvs_p": "p.Gln1756Profs*74",
        "consequence": "frameshift_variant",
        "allele_frequency_gnomad": 0.00001,
        "is_gene_lof_mechanism": True,
        "alphamissense_score": 0.95,
        "cadd_phred": 32.0,
        "revel_score": 0.88,
    }

    result = engine.evaluate_variant(variant)
    assert result["acmg_class"] in ["PATHOGENIC", "LIKELY_PATHOGENIC"]
    assert result["pathogenicity_score"] >= 0.90
    assert any(c["criterion_code"] == "PVS1" for c in result["criteria"])
    assert any(c["criterion_code"] == "PM2" for c in result["criteria"])
    assert len(result["predictor_scores"]) == 4


def test_evaluate_benign_common_variant():
    engine = VariantPathogenicityEngine()
    variant = {
        "gene_symbol": "CFTR",
        "hgvs_c": "c.1408A>G",
        "hgvs_p": "p.Met470Val",
        "consequence": "synonymous_variant",
        "allele_frequency_gnomad": 0.45,
        "is_gene_lof_mechanism": True,
        "alphamissense_score": 0.10,
        "cadd_phred": 8.0,
        "revel_score": 0.15,
        "spliceai_delta_score": 0.01,
    }

    result = engine.evaluate_variant(variant)
    assert result["acmg_class"] in ["BENIGN", "LIKELY_BENIGN"]
    assert result["pathogenicity_score"] <= 0.10
    assert any(c["criterion_code"] == "BA1" for c in result["criteria"])


def test_evaluate_missense_hotspot():
    engine = VariantPathogenicityEngine()
    variant = {
        "gene_symbol": "TP53",
        "hgvs_c": "c.743G>A",
        "hgvs_p": "p.Arg248Gln",
        "consequence": "missense_variant",
        "allele_frequency_gnomad": 0.000005,
        "in_critical_domain": True,
        "functional_assay_abnormal": True,
        "alphamissense_score": 0.98,
        "cadd_phred": 34.0,
        "revel_score": 0.92,
    }

    result = engine.evaluate_variant(variant)
    assert result["acmg_class"] == "PATHOGENIC"
    assert result["pathogenicity_score"] >= 0.95
    assert any(c["criterion_code"] == "PS3" for c in result["criteria"])
    assert any(c["criterion_code"] == "PM1" for c in result["criteria"])
