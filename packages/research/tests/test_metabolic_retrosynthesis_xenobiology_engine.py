"""Tests for Phase 507: Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

import pytest
from research.orchestration.metabolic_retrosynthesis_xenobiology_engine import MetabolicRetrosynthesisXenobiologyEngine


def test_metabolic_retrosynthesis_xenobiology_engine():
    engine = MetabolicRetrosynthesisXenobiologyEngine()
    result = engine.analyze(
        target_specimen="In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes",
        analytical_modality="xenobiotic-retrosynthesis-flux",
        input_scale=1.0,
    )

    assert result.target_specimen == "In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes"
    assert result.confidence_score >= 0.95
    assert result.retrosynthetic_pathway_plausibility_score != 0.0
    assert result.thermodynamic_driving_force_delta_G_kj_mol != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Non-Natural Xenobio" in result.summary_report
