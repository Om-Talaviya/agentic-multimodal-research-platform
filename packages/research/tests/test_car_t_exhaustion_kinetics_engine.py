"""Tests for Phase 183: CAR-T Cell Exhaustion Engine."""

import pytest
from research.immunology.car_t_exhaustion_kinetics_engine import CARTExhaustionKineticsEngine


def test_car_t_exhaustion_simulation():
    engine = CARTExhaustionKineticsEngine()
    result = engine.simulate_exhaustion_kinetics(
        car_construct_name="anti-CD19-41BBz",
        costimulatory_domain="4-1BB",
        antigen_density=15000.0,
        tonic_signaling_level="low",
        il2_il15_priming_ratio=2.5,
    )

    assert result.car_construct_name == "anti-CD19-41BBz"
    assert result.t_stem_cell_memory_pct > 20.0
    assert result.predicted_persistence_half_life_days > 60.0
    assert len(result.differentiation_states) == 4
    assert len(result.checkpoint_markers) == 3
    assert result.memory_fitness_index > 0.0