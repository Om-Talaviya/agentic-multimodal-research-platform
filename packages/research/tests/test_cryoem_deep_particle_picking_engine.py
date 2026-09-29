"""Tests for Phase 275: Autonomous Deep Learning Cryo-EM Raw Micrograph Particle Picking & Ice Contamination Filter Engine."""

import pytest
from research.orchestration.cryoem_deep_particle_picking_engine import CryoemDeepParticlePickingEngine


def test_cryoem_deep_particle_picking_engine():
    engine = CryoemDeepParticlePickingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-deep-particle-picking",
        input_scale=1.0,
    )
    assert getattr(result, "particle_picking_precision_f1_score") != 0
    assert getattr(result, "ice_contamination_rejection_rate_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
