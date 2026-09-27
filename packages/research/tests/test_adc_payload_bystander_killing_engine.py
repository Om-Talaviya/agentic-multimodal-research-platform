"""Tests for Phase 233: Autonomous Antibody-Drug Conjugate (ADC) Payload Bystander Killing & Lysosomal Cleavability Engine Engine."""

import pytest
from research.orchestration.adc_payload_bystander_killing_engine import AdcPayloadBystanderKillingEngine


def test_adc_payload_bystander_killing_engine():
    engine = AdcPayloadBystanderKillingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="adc-payload-bystander-killing",
        input_scale=1.0,
    )
    assert getattr(result, "bystander_cytotoxicity_index") != 0
    assert getattr(result, "cleavage_rate_constant_kcat_over_km") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
