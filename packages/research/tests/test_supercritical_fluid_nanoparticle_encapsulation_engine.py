"""Tests for Phase 555: Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

import pytest
from research.orchestration.supercritical_fluid_nanoparticle_encapsulation_engine import SupercriticalFluidNanoparticleEncapsulationEngine


def test_supercritical_fluid_nanoparticle_encapsulation_engine():
    engine = SupercriticalFluidNanoparticleEncapsulationEngine()
    result = engine.analyze(
        target_specimen="Supercritical CO2 Rapid Expansion (RESS-SC) of PLGA-PEG Encapsulating Hydrophobic Paclitaxel and Cy5.5 Nanotracers",
        analytical_modality="supercritical-fluid-nanoparticle",
        input_scale=1.0,
    )

    assert result.target_specimen == "Supercritical CO2 Rapid Expansion (RESS-SC) of PLGA-PEG Encapsulating Hydrophobic Paclitaxel and Cy5.5 Nanotracers"
    assert result.confidence_score >= 0.95
    assert result.nanoparticle_mean_hydrodynamic_diameter_nm != 0.0
    assert result.encapsulation_efficiency_payload_pct != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Microfluidic High-P" in result.summary_report
