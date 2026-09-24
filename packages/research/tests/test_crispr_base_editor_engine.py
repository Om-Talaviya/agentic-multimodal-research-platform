"""
Engine tests for Phase 164: CRISPR Base Editor.
"""

from research.gene_editing.crispr_base_editor_engine import CRISPRBaseEditorEngine


def test_crispr_base_editor_engine():
    engine = CRISPRBaseEditorEngine()
    result = engine.predict_editing_profile(
        target_gene="HBB",
        protospacer_sequence="GAACACCCAGAGCCCGGACG",
        editor_type="ABE8e",
        pam="NGG",
    )

    assert result.target_gene == "HBB"
    assert result.editor_type == "ABE8e"
    assert result.on_target_efficiency > 0.0
    assert result.bystander_purity_score > 0.0
    assert len(result.transitions) > 0
    assert len(result.bystander_windows) > 0
    assert len(result.recommendations) >= 2
