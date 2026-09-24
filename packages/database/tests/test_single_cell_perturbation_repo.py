"""
Database repository tests for Phase 167: Single Cell Perturbation.
"""

import pytest
from database.repositories.single_cell_perturbation_repo import SingleCellPerturbationRepository


@pytest.mark.asyncio
async def test_single_cell_perturbation_repo_lifecycle(db_session):
    repo = SingleCellPerturbationRepository(db_session)

    study = await repo.create_study(
        study_name="K562_PerturbSeq_Test",
        perturbation_modality="CRISPRi-PerturbSeq",
        total_cells_profiled=9600,
        target_genes_count=4,
        energy_distance_shift=3.85,
        causal_network_density=0.64,
    )
    assert study.id is not None
    assert study.study_name == "K562_PerturbSeq_Test"

    effect = await repo.add_target_effect(
        study_id=study.id,
        guide_target_gene="MYC",
        knockdown_efficiency_percent=92.5,
        differentially_expressed_genes_count=260,
        phenotypic_dispersion_score=1.87,
    )
    assert effect.id is not None
    assert effect.guide_target_gene == "MYC"

    edge = await repo.add_grn_edge(
        study_id=study.id,
        source_regulator_gene="MYC",
        target_effector_gene="CDK4",
        causal_weight_beta=0.74,
        p_value_fdr=1.2e-8,
        regulation_sign="Activation",
    )
    assert edge.id is not None
    assert edge.source_regulator_gene == "MYC"

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert len(fetched.target_effects) == 1
    assert len(fetched.grn_edges) == 1
