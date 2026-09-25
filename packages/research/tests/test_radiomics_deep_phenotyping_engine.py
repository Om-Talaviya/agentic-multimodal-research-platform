import pytest
from research.imaging.radiomics_deep_phenotyping_engine import RadiomicsDeepPhenotypingEngine

def test_radiomics_deep_phenotyping_engine():
    engine = RadiomicsDeepPhenotypingEngine()
    result = engine.simulate_radiomics_extraction(
        scan_modality="Multiparametric MRI",
        tumor_type="Glioblastoma Multiforme",
        gross_tumor_volume_cm3=48.5,
        intratumoral_heterogeneity_input=0.89,
    )
    assert result.gross_tumor_volume_cm3 == 48.5
    assert len(result.habitat_subregions) == 3
    assert len(result.texture_features) >= 4
    assert result.predicted_overall_survival_months > 0
    assert result.imaging_biomarker_score > 0
