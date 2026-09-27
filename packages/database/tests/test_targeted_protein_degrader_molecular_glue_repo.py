"""Tests for Phase 236: Autonomous Molecular Glue Degrader (MGD) CRBN/VHL Ternary Composite Cooperativity Engine Repo."""

import pytest
from database.repositories.targeted_protein_degrader_molecular_glue_repo import TargetedProteinDegraderMolecularGlueRepository


@pytest.mark.asyncio
async def test_targeted_protein_degrader_molecular_glue_repository(db_session):
    repo = TargetedProteinDegraderMolecularGlueRepository(db_session)

    study = await repo.create_study(
        name="Study_236_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="targeted-protein-degrader-molecular-glue",
        cooperativity_alpha_factor=24.5,
        degradation_dc50_nM=8.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 236 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_236_Verification"
    assert getattr(study, "cooperativity_alpha_factor") == 24.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Lenalidomide_CRBN_IKZF1_Ternary_Interface",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Lenalidomide_CRBN_IKZF1_Ternary_Interface"

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
    assert fetched.name == "Study_236_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
