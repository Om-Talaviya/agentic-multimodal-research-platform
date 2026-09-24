"""
Engine tests for Phase 167: Single Cell Perturbation.
"""

from research.single_cell.single_cell_perturbation_engine import SingleCellPerturbationEngine


def test_single_cell_perturbation_engine():
    engine = SingleCellPerturbationEngine()
    result = engine.analyze_perturbation_screen(
        study_name="Immune_PerturbSeq",
        modality="CRISPRa-PerturbSeq",
        target_genes=["STAT3", "NFKB1", "GATA3"],
    )

    assert result.study_name == "Immune_PerturbSeq"
    assert result.total_cells == 7200
    assert result.targets_count == 3
    assert result.e_distance > 0.0
    assert len(result.target_effects) == 3
    assert len(result.grn_edges) > 0
    assert len(result.recommendations) >= 2
