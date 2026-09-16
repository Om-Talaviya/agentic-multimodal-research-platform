"""
Tests for Phase 59: ADC Engine.
"""
from research.adc.adc_engine import ADCDesignEngine


def test_screen_payload_linkers():
    res = ADCDesignEngine.screen_payload_linkers(
        antibody_name="Trastuzumab",
        target_antigen="HER2",
        target_dar=8.0,
    )
    assert len(res) >= 5
    for c in res:
        assert "construct_code" in c
        assert "therapeutic_index_score" in c
        assert c["measured_dar"] > 0
