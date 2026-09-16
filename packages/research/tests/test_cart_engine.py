import pytest
from research.cart.cart_engine import CARTEngine

def test_car_design():
    engine = CARTEngine()
    res = engine.design_car_construct("Kymriah-Clone", "CD19", "4-1BB")
    assert res["target_antigen"] == "CD19"
    assert res["scfv_binder_clone"] == "FMC63"
    assert "Leader" not in res["full_aa_sequence"] or "_" in res["full_aa_sequence"]

def test_cytotoxicity_simulation():
    engine = CARTEngine()
    res = engine.simulate_cytotoxicity("CD19", "4-1BB", "Raji", 5.0)
    assert res["specific_lysis_pct"] > 60.0
    assert res["t_cell_persistence_score"] > 0.5
    assert res["cytotoxicity_grade"] in ["POTENT", "HIGH"]

def test_crs_toxicity_prediction():
    engine = CARTEngine()
    res = engine.predict_crs_toxicity("CD19", "4-1BB", tumor_burden_index=1.0)
    assert res["peak_il6_pg_ml"] > 0
    assert res["astct_crs_grade_predicted"] in ["Grade 1", "Grade 2", "Grade 3", "Grade 4"]
