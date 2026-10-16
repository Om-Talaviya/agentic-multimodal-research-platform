"""Tests for Phase 566: Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor Repo."""

import pytest
from database.repositories.rna_targeted_adar_deaminase_editing_repo import RnaTargetedAdarDeaminaseEditingRepository


@pytest.mark.asyncio
async def test_rna_targeted_adar_deaminase_editing_repository(db_session):
    repo = RnaTargetedAdarDeaminaseEditingRepository(db_session)

    study = await repo.create_study(
        name="Study_566_Verification",
        target_specimen="Endogenous Human ADAR2 Deaminase recruited via Circular Guide RNA (arRNA) targeting Premature Stop Codons in MECP2 mRNA",
        analytical_modality="programmable-adar-rna-editing",
        targeted_adenosine_to_inosine_editing_efficiency_pct=78.4,
        bystander_adenosine_deamination_rate_pct=2.1,
        guide_circular_rna_stability_half_life_hours=48.0,
        target_transcript_restoration_fold=12.5,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 566 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_566_Verification"
    assert study.targeted_adenosine_to_inosine_editing_efficiency_pct == 78.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Target_A_to_I_Deamination_Mismatch_Bulge_Loop",
        profile_category="Primary Step",
        quantitative_value=78.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Target_A_to_I_Deamination_Mismatch_Bulge_Loop"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="targeted_adenosine_to_inosine_editing_efficiency_pct",
        observed_value=78.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 78.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_566_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
