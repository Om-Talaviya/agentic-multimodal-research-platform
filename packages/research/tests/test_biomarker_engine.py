"""Tests for Biomarker Signature Extractor Engine."""
import pytest
from research.biomarkers.biomarker_engine import BiomarkerSignatureExtractorEngine


def test_biomarker_signature_extraction_default():
    engine = BiomarkerSignatureExtractorEngine()
    result = engine.extract_signature({
        "study_title": "NSCLC Immunotherapy Trial",
        "disease_indication": "NSCLC",
        "cohort_sample_size": 200,
        "omics_layers": ["TRANSCRIPTOMICS", "PROTEOMICS", "EPIGENOMICS", "METABOLOMICS"]
    })

    assert result["study_title"] == "NSCLC Immunotherapy Trial"
    assert result["disease_indication"] == "NSCLC"
    assert result["cohort_sample_size"] == 200
    assert result["auc_roc_score"] > 0.8
    assert result["signature_stability_score"] > 0.7
    assert len(result["features"]) >= 4
    assert len(result["stratifications"]) == 3


def test_biomarker_signature_extraction_custom_features():
    engine = BiomarkerSignatureExtractorEngine()
    custom_features = [
        {
            "feature_name": "FOXP3",
            "omics_modality": "TRANSCRIPTOMICS",
            "log2_fold_change": -2.1,
            "adjusted_p_value": 0.002,
            "feature_importance_weight": 0.88,
            "correlation_direction": "NEGATIVE",
        }
    ]
    result = engine.extract_signature(
        study_input={"study_title": "Treg Infiltration Signature"},
        raw_features=custom_features,
    )

    assert result["study_title"] == "Treg Infiltration Signature"
    assert len(result["features"]) == 1
    assert result["features"][0]["feature_name"] == "FOXP3"
