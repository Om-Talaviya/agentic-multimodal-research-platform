"""Tests for Phase 267: Autonomous In-Vivo CAR-T Cell In-Situ Reprogramming & Retargeting Tropism Vector Simulator Engine."""

import pytest
from research.orchestration.in_vivo_cart_reprogramming_tropism_engine import InVivoCartReprogrammingTropismEngine


def test_in_vivo_cart_reprogramming_tropism_engine():
    engine = InVivoCartReprogrammingTropismEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="in-vivo-cart-reprogramming-tropism",
        input_scale=1.0,
    )
    assert getattr(result, "in_vivo_t_cell_transduction_selectivity_fold") != 0
    assert getattr(result, "hepatic_off_target_accumulation_reduction_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
