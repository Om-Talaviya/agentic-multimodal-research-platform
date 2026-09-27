"""Tests for Phase 230: Autonomous siRNA Phosphorothioate & 2-O-Methyl Stability Optimization Engine Engine."""

import pytest
from research.orchestration.sirna_chemical_modification_ps_ome_engine import SirnaChemicalModificationPsOmeEngine


def test_sirna_chemical_modification_ps_ome_engine():
    engine = SirnaChemicalModificationPsOmeEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="sirna-chemical-modification-ps-ome",
        input_scale=1.0,
    )
    assert getattr(result, "serum_half_life_exonuclease_hours") != 0
    assert getattr(result, "tlr7_8_immune_quiescence_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
