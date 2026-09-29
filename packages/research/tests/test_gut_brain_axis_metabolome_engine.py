"""Tests for Phase 364: Autonomous Microbiome-Gut-Brain Axis Metabolite Signaling & Neuroactive Neurotransmitter Modeler Engine."""

import pytest
from research.orchestration.gut_brain_axis_metabolome_engine import GutBrainAxisMetabolomeEngine


def test_gut_brain_axis_metabolome_engine():
    engine = GutBrainAxisMetabolomeEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="gut-brain-axis-metabolome",
        input_scale=1.0,
    )
    assert getattr(result, "neuroactive_metabolite_synthesis_rate_umol_hr") != 0
    assert getattr(result, "blood_brain_barrier_integrity_enhancement_fold") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
