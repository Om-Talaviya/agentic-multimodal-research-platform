import pytest
from research.flow_cytometry.flow_cytometry_engine import FlowCytometryGatingEngine

def test_flow_cytometry_engine_z_prime_and_gating():
    engine = FlowCytometryGatingEngine()

    # 1. Test Z'-factor calculation
    pos_ctrls = [95.2, 94.8, 96.1, 95.0, 94.4]
    neg_ctrls = [4.1, 3.9, 4.3, 4.0, 3.8]
    z_res = engine.calculate_z_prime_factor(pos_ctrls, neg_ctrls)
    assert z_res["z_prime_factor"] >= 0.75
    assert z_res["assay_quality_status"] == "EXCELLENT_ASSAY"
    assert z_res["signal_to_background"] > 10.0

    # 2. Test Point in Polygon Algorithm
    square_poly = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
    assert engine.is_point_in_polygon(5.0, 5.0, square_poly) is True
    assert engine.is_point_in_polygon(15.0, 5.0, square_poly) is False

    # 3. Test Hierarchical Gating
    steps = [
        {"gate_name": "Lymphocytes", "synthetic_retention_rate": 0.80},
        {"gate_name": "Singlets", "synthetic_retention_rate": 0.90},
        {"gate_name": "CD8+ T Cells", "synthetic_retention_rate": 0.70},
    ]
    gating_tree = engine.execute_hierarchical_gating(total_event_count=50000, gating_steps=steps)
    assert len(gating_tree) == 3
    assert gating_tree[0]["gated_event_count"] == 40000
    assert gating_tree[1]["gated_event_count"] == 36000
    assert gating_tree[2]["gated_event_count"] == 25200
