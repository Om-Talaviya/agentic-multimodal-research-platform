"""Tests for Phase 409: Autonomous Targeted RNA Degradation (RIBOTAC) Small Molecule RNase L Recruiter Repo."""

import pytest
from database.repositories.targeted_rna_degradation_ribotac_repo import TargetedRnaDegradationRibotacRepository


@pytest.mark.asyncio
async def test_targeted_rna_degradation_ribotac_repository(db_session):
    repo = TargetedRnaDegradationRibotacRepository(db_session)

    study = await repo.create_study(
        name="Study_409_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="targeted-rna-degradation-ribotac",
        target_rna_transcript_cleavage_efficiency_pct=87.4,
        rnase_l_dimerization_activation_selectivity_fold=65.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 409 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_409_Verification"
    assert getattr(study, "target_rna_transcript_cleavage_efficiency_pct") == 87.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="miR_21_Hairpin_Binding_Bis_Benzimidazole_Conjugate",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "miR_21_Hairpin_Binding_Bis_Benzimidazole_Conjugate"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_409_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
