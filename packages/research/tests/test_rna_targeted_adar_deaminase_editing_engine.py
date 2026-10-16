"""Tests for Phase 566: Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

import pytest
from research.orchestration.rna_targeted_adar_deaminase_editing_engine import RnaTargetedAdarDeaminaseEditingEngine


def test_rna_targeted_adar_deaminase_editing_engine():
    engine = RnaTargetedAdarDeaminaseEditingEngine()
    result = engine.analyze(
        target_specimen="Endogenous Human ADAR2 Deaminase recruited via Circular Guide RNA (arRNA) targeting Premature Stop Codons in MECP2 mRNA",
        analytical_modality="programmable-adar-rna-editing",
        input_scale=1.0,
    )

    assert result.target_specimen == "Endogenous Human ADAR2 Deaminase recruited via Circular Guide RNA (arRNA) targeting Premature Stop Codons in MECP2 mRNA"
    assert result.confidence_score >= 0.95
    assert result.targeted_adenosine_to_inosine_editing_efficiency_pct != 0.0
    assert result.bystander_adenosine_deamination_rate_pct != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Programmable RNA-Ta" in result.summary_report
