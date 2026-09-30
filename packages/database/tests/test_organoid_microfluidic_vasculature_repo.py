"""Tests for Phase 406: Autonomous 3D Organoid Perfusable Microfluidic Endothelial Vasculature Simulator Repo."""

import pytest
from database.repositories.organoid_microfluidic_vasculature_repo import OrganoidMicrofluidicVasculatureRepository


@pytest.mark.asyncio
async def test_organoid_microfluidic_vasculature_repository(db_session):
    repo = OrganoidMicrofluidicVasculatureRepository(db_session)

    study = await repo.create_study(
        name="Study_406_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="organoid-microfluidic-vasculature",
        vascular_perfusion_lumen_patency_pct=95.8,
        fluid_shear_stress_endothelial_alignment_dyn_cm2=14.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 406 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_406_Verification"
    assert getattr(study, "vascular_perfusion_lumen_patency_pct") == 95.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="HUVEC_Pericyte_Co_Culture_Microvascular_Network_Mesh",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "HUVEC_Pericyte_Co_Culture_Microvascular_Network_Mesh"

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
    assert fetched.name == "Study_406_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
