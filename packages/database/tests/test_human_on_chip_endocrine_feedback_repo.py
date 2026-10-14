"""Tests for Phase 492: Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop Repo."""

import pytest
from database.repositories.human_on_chip_endocrine_feedback_repo import HumanOnChipEndocrineFeedbackRepository


@pytest.mark.asyncio
async def test_human_on_chip_endocrine_feedback_repository(db_session):
    repo = HumanOnChipEndocrineFeedbackRepository(db_session)

    study = await repo.create_study(
        name="Study_492_Verification",
        target_specimen="4-Organ Interconnected Microfluidic Platform (Liver Spheroids, Islet Organoids, Adipose, Skeletal Muscle)",
        analytical_modality="human-on-chip-endocrine-loop",
        glucose_stimulated_insulin_secretion_gsis_index=3.85,
        hepatic_glucose_uptake_rate_uM_per_hr=42.0,
        inter_organ_circulatory_perfusion_flow_uL_per_min=5.0,
        homeostatic_endocrine_feedback_sync_tau=0.985,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 492 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_492_Verification"
    assert study.glucose_stimulated_insulin_secretion_gsis_index == 3.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Pancreatic_Beta_Cell_Islet_Insulin_Perfusion_Loop",
        profile_category="Primary Step",
        quantitative_value=3.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Pancreatic_Beta_Cell_Islet_Insulin_Perfusion_Loop"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="glucose_stimulated_insulin_secretion_gsis_index",
        observed_value=3.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_492_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
