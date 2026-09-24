"""Tests for CFPSTXTLEngine (Phase 157)."""

from research.synthetic_biology.cfps_txtl_engine import (
    CFPSTXTLEngine,
    CFPSTXTLRequest,
)


def test_cfps_txtl_engine():
    engine = CFPSTXTLEngine()
    req = CFPSTXTLRequest(
        target_protein_name="Interleukin-2 Cytokine",
        extract_system_type="E. coli Cell-Free Lysate",
        reaction_mode="Continuous Exchange",
        dna_template_concentration_nM=10.0,
        reaction_temperature_celsius=30.0,
    )
    result = engine.simulate_tx_tl(req)
    assert result.final_protein_yield_mg_ml > 1.0
    assert result.transcription_rate_nt_s > 0
    assert len(result.yield_trajectories) == 7
    assert len(result.substrate_depletions) == 3
