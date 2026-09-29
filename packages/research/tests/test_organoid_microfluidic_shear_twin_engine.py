"""Tests for Phase 341: Autonomous In Silico Organoid Microfluidic Shear Stress & Nutrient Diffusion Twin Engine."""

import pytest
from research.orchestration.organoid_microfluidic_shear_twin_engine import OrganoidMicrofluidicShearTwinEngine


def test_organoid_microfluidic_shear_twin_engine():
    engine = OrganoidMicrofluidicShearTwinEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="organoid-microfluidic-twin",
        input_scale=1.0,
    )
    assert getattr(result, "physiologic_wall_shear_stress_dynes_cm2") != 0
    assert getattr(result, "core_hypoxia_volume_fraction_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
