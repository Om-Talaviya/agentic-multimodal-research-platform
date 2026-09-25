"""Tests for Phase 178: ADC DAR Optimization Engine."""

import pytest
from research.biologics.adc_dar_optimization_engine import ADCDAROptimizationEngine


def test_adc_dar_optimization_simulation():
    engine = ADCDAROptimizationEngine()
    result = engine.simulate_dar_optimization(
        antibody_name="Trastuzumab",
        payload_name="MMAE",
        target_dar=4.0,
        linker_type="cleavable_val_cit",
        conjugation_chemistry="cysteine_maleimide",
        payload_logp=2.8,
        reaction_stoichiometry=4.5,
    )

    assert result.antibody_name == "Trastuzumab"
    assert result.payload_name == "MMAE"
    assert 2.0 <= result.calculated_mean_dar <= 6.0
    assert result.aggregation_propensity_score >= 0.0
    assert len(result.species_distribution) > 0
    assert len(result.aggregation_kinetics) == 5
    assert result.therapeutic_index_multiplier > 0.0
