"""Tests for Fragmentomics MRD Engine."""
import pytest
from research.liquid_biopsy.fragmentomics_engine import FragmentomicsMRDEngine


def test_analyze_sample_mrd_positive():
    engine = FragmentomicsMRDEngine()
    sample_input = {
        "patient_id": "PT-CRC-500",
        "sample_barcode": "LB-500-POST",
        "cancer_type": "Colorectal Cancer",
        "sampling_timepoint": "POST_SURGERY",
        "total_cfdna_ng_ml": 18.5,
        "short_fragments_100_150bp": 45000,
        "long_fragments_160_220bp": 95000,
    }

    result = engine.analyze_sample(sample_input)
    assert result["mrd_status"] == "MRD_POSITIVE"
    assert result["tumor_fraction_pct"] >= 0.10
    assert result["fragment_short_ratio"] >= 0.30
    assert len(result["size_distributions"]) == 6
    assert len(result["end_motifs"]) == 5
    assert result["sample_metadata_json"]["relapse_risk_probability"] >= 0.50


def test_analyze_sample_mrd_negative():
    engine = FragmentomicsMRDEngine()
    sample_input = {
        "patient_id": "PT-HEALTHY-01",
        "sample_barcode": "LB-CTRL-01",
        "cancer_type": "None / Healthy Control",
        "sampling_timepoint": "ROUTINE",
        "total_cfdna_ng_ml": 5.0,
        "short_fragments_100_150bp": 15000,
        "long_fragments_160_220bp": 100000,
    }

    result = engine.analyze_sample(sample_input)
    assert result["mrd_status"] == "MRD_NEGATIVE"
    assert result["tumor_fraction_pct"] <= 0.05
    assert result["fragment_short_ratio"] <= 0.20
    assert result["sample_metadata_json"]["relapse_risk_probability"] <= 0.10
