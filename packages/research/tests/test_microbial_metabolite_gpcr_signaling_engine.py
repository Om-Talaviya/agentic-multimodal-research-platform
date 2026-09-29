"""Tests for Phase 304: Autonomous Multi-Omics Microbially-Derived Metabolite Host GPCR Signal Transduction & Immunomodulation Modeler Engine."""

import pytest
from research.orchestration.microbial_metabolite_gpcr_signaling_engine import MicrobialMetaboliteGpcrSignalingEngine


def test_microbial_metabolite_gpcr_signaling_engine():
    engine = MicrobialMetaboliteGpcrSignalingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microbial-metabolite-gpcr-signaling",
        input_scale=1.0,
    )
    assert getattr(result, "host_gpcr_activation_potency_ec50_uM") != 0
    assert getattr(result, "treg_polarization_induction_fold") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
