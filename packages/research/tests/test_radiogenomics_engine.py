"""Tests for RadiogenomicsEngine."""
import pytest
from research.imaging.radiogenomics_engine import RadiogenomicsEngine


def test_radiogenomics_engine_brain_glioma():
    engine = RadiogenomicsEngine()
    result = engine.extract_radiomic_features(
        patient_id="TCGA-02-0001",
        modality="MRI_T1_CONTRAST",
        anatomical_region="BRAIN_GLIOMA",
        lesion_volume_cm3=28.0,
    )

    assert "scan" in result
    assert result["scan"]["patient_id"] == "TCGA-02-0001"
    assert result["scan"]["lesion_volume_cm3"] == 28.0

    assert "radiomic_features" in result
    assert len(result["radiomic_features"]) >= 7
    families = [f["family"] for f in result["radiomic_features"]]
    assert "IBSI_SHAPE_3D" in families
    assert "IBSI_GLCM_TEXTURE" in families

    assert "genomic_correlations" in result
    assert len(result["genomic_correlations"]) >= 1
    mutations = [c["predicted_genomic_alteration"] for c in result["genomic_correlations"]]
    assert "IDH1_R132H" in mutations


def test_radiogenomics_engine_lung_nsclc():
    engine = RadiogenomicsEngine()
    result = engine.extract_radiomic_features(
        patient_id="TCGA-LUAD-05",
        modality="CT_CHEST_CONTRAST",
        anatomical_region="LUNG_NSCLC",
    )

    mutations = [c["predicted_genomic_alteration"] for c in result["genomic_correlations"]]
    assert "EGFR_EXON19_DEL" in mutations
