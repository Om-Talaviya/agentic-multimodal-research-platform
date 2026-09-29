"""Tests for Phase 325: Autonomous Tara-Oceans Scale Marine Microbial Metatranscriptomic Carbon Export & Nitrogen Flux Predictor Engine."""

import pytest
from research.orchestration.ocean_metatranscriptome_carbon_flux_engine import OceanMetatranscriptomeCarbonFluxEngine


def test_ocean_metatranscriptome_carbon_flux_engine():
    engine = OceanMetatranscriptomeCarbonFluxEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="ocean-metatranscriptome-carbon-flux",
        input_scale=1.0,
    )
    assert getattr(result, "carbon_export_flux_prediction_score_pct") != 0
    assert getattr(result, "particulate_organic_carbon_flux_mg_c_m2_day") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
