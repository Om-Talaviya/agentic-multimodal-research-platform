"""Tests for Phase 552: Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

import pytest
from research.orchestration.denovo_rbs_translation_initiation_optimizer_engine import DenovoRbsTranslationInitiationOptimizerEngine


def test_denovo_rbs_translation_initiation_optimizer_engine():
    engine = DenovoRbsTranslationInitiationOptimizerEngine()
    result = engine.analyze(
        target_specimen="Synthetic mRNA Polycistronic Operon 5' UTR Shine-Dalgarno Core Library in Escherichia coli BL21(DE3)",
        analytical_modality="de-novo-rbs-optimization",
        input_scale=1.0,
    )

    assert result.target_specimen == "Synthetic mRNA Polycistronic Operon 5' UTR Shine-Dalgarno Core Library in Escherichia coli BL21(DE3)"
    assert result.confidence_score >= 0.95
    assert result.translation_initiation_rate_arbitrary_units != 0.0
    assert result.rna_secondary_structure_free_energy_kcal_mol != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Deep Learning De No" in result.summary_report
