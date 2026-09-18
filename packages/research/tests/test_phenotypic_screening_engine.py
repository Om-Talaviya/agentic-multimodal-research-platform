"""Tests for PhenotypicScreeningEngine."""

import pytest
from research.imaging.phenotypic_screening_engine import PhenotypicScreeningEngine


def test_phenotypic_screening_engine_analysis():
    engine = PhenotypicScreeningEngine()

    # 1. Analyze active compound well
    res = engine.analyze_well_morphology(
        well_position="C05",
        compound_name="Nocodazole",
        concentration_uM=10.0,
        is_control=False,
    )
    assert res["well_position"] == "C05"
    assert res["compound_name"] == "Nocodazole"
    assert res["phenotypic_activity_score"] >= 0.0
    assert "predicted_moa" in res
    assert 0.0 <= res["moa_confidence"] <= 1.0
    assert "morphological_profile" in res
    assert len(res["single_cells"]) > 0


def test_phenotypic_screening_engine_control():
    engine = PhenotypicScreeningEngine()

    # 2. Analyze DMSO control well
    res_ctrl = engine.analyze_well_morphology(
        well_position="A01",
        compound_name="DMSO",
        concentration_uM=0.1,
        is_control=True,
    )
    assert res_ctrl["predicted_moa"] == "Negative Control / Vehicle"
    assert res_ctrl["moa_confidence"] >= 0.90
    assert res_ctrl["phenotypic_activity_score"] <= 1.0
