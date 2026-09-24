"""
Database repository tests for Phase 164: CRISPR Base Editor.
"""

import pytest
from database.repositories.crispr_base_editor_repo import CRISPRBaseEditorRepository


@pytest.mark.asyncio
async def test_crispr_base_editor_repo_lifecycle(db_session):
    repo = CRISPRBaseEditorRepository(db_session)

    study = await repo.create_study(
        target_gene="PCSK9",
        editor_type="ABE8e",
        protospacer_sequence="GAACACCCAGAGCCCGGACG",
        pam_sequence="NGG",
        on_target_conversion_efficiency=0.82,
        bystander_purity_score=0.91,
    )
    assert study.id is not None
    assert study.target_gene == "PCSK9"

    trans = await repo.add_transition(
        study_id=study.id,
        protospacer_position=6,
        initial_base="A",
        target_base="G",
        transition_efficiency=0.82,
        amino_acid_consequence="Target Missense Correction (Arg->Gln)",
    )
    assert trans.id is not None
    assert trans.protospacer_position == 6

    bw = await repo.add_bystander_window(
        study_id=study.id,
        window_range="Positions 4-8",
        bystander_count=1,
        unintended_mutation_risk_percent=4.2,
        mitigation_strategy="Deploy narrow-window deaminase variant",
    )
    assert bw.id is not None
    assert bw.bystander_count == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert len(fetched.transitions) == 1
    assert len(fetched.bystander_windows) == 1
