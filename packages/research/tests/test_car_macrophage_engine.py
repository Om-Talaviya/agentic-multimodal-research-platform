import pytest
from research.immunology.car_macrophage_engine import (
    CARMacrophageEngine,
    CARMacrophageInput,
)


def test_car_macrophage_engine_modeling():
    engine = CARMacrophageEngine()
    result = engine.model_car_macrophage_activity(
        construct_name="CT-0508 Anti-HER2 CAR-M",
        target_antigen="HER2",
        signaling_domain="Megf10 / FcR-gamma",
        tumor_type="Metastatic Breast Carcinoma",
    )

    assert result.construct_name == "CT-0508 Anti-HER2 CAR-M"
    assert result.target_antigen == "HER2"
    assert result.overall_phagocytosis_efficiency_percent > 70.0
    assert result.whole_cell_engulfment_percent > 50.0
    assert result.antigen_cross_presentation_score == 0.89
    assert result.matrix_metalloproteinase_activity["mmp9_collagenase_secretion_ng_ml"] == 820.0
    assert len(result.recommendations) == 3
