"""Tests for Phase 261: Autonomous Deep Generative Antibody De-Immunization & T-Cell Epitope Elimination Engine Repo."""

import pytest
from database.repositories.antibody_deimmunization_epitope_removal_repo import AntibodyDeimmunizationEpitopeRemovalRepository


@pytest.mark.asyncio
async def test_antibody_deimmunization_epitope_removal_repository(db_session):
    repo = AntibodyDeimmunizationEpitopeRemovalRepository(db_session)

    study = await repo.create_study(
        name="Study_261_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="antibody-deimmunization-epitope-removal",
        t_cell_epitope_depletion_efficiency_pct=96.4,
        binding_affinity_retention_ratio=0.98,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 261 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_261_Verification"
    assert getattr(study, "t_cell_epitope_depletion_efficiency_pct") == 96.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Anti_EGFR_Chimeric_mAb_CD4_T_Cell_Epitope_Removal",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Anti_EGFR_Chimeric_mAb_CD4_T_Cell_Epitope_Removal"

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
    assert fetched.name == "Study_261_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
