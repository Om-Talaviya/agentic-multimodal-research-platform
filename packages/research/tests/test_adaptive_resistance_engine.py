"""Tests for AdaptiveResistanceEngine."""

import pytest
from research.oncology.adaptive_resistance_engine import (
    AdaptiveResistanceEngine,
    ClonalSpecification,
    DosingRegimenStep,
)


def test_adaptive_resistance_simulation_flow():
    engine = AdaptiveResistanceEngine(carrying_capacity=1e9)

    clones = [
        ClonalSpecification(
            clone_name="Clone_WT",
            driver_mutations=["TP53_mut"],
            initial_frequency=0.8,
            intrinsic_growth_rate=0.04,
            ic50=5.0,
            phenotype="SENSITIVE",
        ),
        ClonalSpecification(
            clone_name="Clone_Resistant_ABCB1",
            driver_mutations=["TP53_mut", "ABCB1_amp"],
            initial_frequency=0.2,
            intrinsic_growth_rate=0.035,
            ic50=50.0,
            phenotype="MULTI_DRUG_RESISTANT",
        ),
    ]

    regimen = [
        DosingRegimenStep(
            drug_name="Doxorubicin",
            dosage=30.0,
            duration_days=5,
            holiday_days=16,
        )
    ]

    result = engine.simulate_treatment_course(
        study_name="Breast Cancer Adaptive Doxorubicin Study",
        cancer_type="Invasive Ductal Carcinoma",
        clones=clones,
        regimen=regimen,
        cycles=4,
        adaptive_threshold=0.6,
    )

    assert result.study_name == "Breast Cancer Adaptive Doxorubicin Study"
    assert result.total_days == 4 * 21  # 84 days
    assert len(result.trajectories) == 4
    assert len(result.final_clones) == 2
    assert "final_burden" in result.summary_metrics
    assert "max_resistance_index" in result.summary_metrics
    assert result.summary_metrics["total_cycles_simulated"] == 4
    assert len(result.recommendations) > 0
