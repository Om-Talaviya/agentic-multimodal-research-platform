"""Tests for Phase 376: Autonomous Riboswitch-Targeting RNA Small-Molecule Kinetic Binding & Conformation Assayer Engine."""

import pytest
from research.orchestration.riboswitch_rna_ligand_binding_engine import RiboswitchRnaLigandBindingEngine


def test_riboswitch_rna_ligand_binding_engine():
    engine = RiboswitchRnaLigandBindingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="riboswitch-rna-ligand-binding",
        input_scale=1.0,
    )
    assert getattr(result, "rna_small_molecule_binding_affinity_apparent_kd_nm") != 0
    assert getattr(result, "transcriptional_attenuation_dynamic_range_fold") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
