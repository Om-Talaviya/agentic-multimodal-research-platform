"""Tests for Phase 220: Autonomous Single-Cell RNA Velocity Lineage Trajectory & CAR-T Epigenetic Exhaustion Interceptor Engine Engine."""

import pytest
from research.orchestration.car_t_exhaustion_scvelo_engine import CarTExhaustionScveloEngine


def test_car_t_exhaustion_scvelo_engine():
    engine = CarTExhaustionScveloEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="car-t-exhaustion-scvelo",
        input_scale=1.0,
    )
    assert getattr(result, "exhaustion_diversion_efficiency_pct") != 0
    assert getattr(result, "stem_memory_persistence_index") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
