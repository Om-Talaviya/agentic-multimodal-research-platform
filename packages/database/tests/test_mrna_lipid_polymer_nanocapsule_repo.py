"""Tests for Phase 354: Autonomous Programmable mRNA Lipid-Polymer Hybrid Nanocapsule Biodistribution & In Vivo Kinetics Engine Repo."""

import pytest
from database.repositories.mrna_lipid_polymer_nanocapsule_repo import MrnaLipidPolymerNanocapsuleRepository


@pytest.mark.asyncio
async def test_mrna_lipid_polymer_nanocapsule_repository(db_session):
    repo = MrnaLipidPolymerNanocapsuleRepository(db_session)

    study = await repo.create_study(
        name="Study_354_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mrna-lipid-polymer-nanocapsule",
        blood_brain_barrier_transcytosis_efficiency_pct=14.8,
        payload_encapsulation_stability_half_life_days=45.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 354 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_354_Verification"
    assert getattr(study, "blood_brain_barrier_transcytosis_efficiency_pct") == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Transferrin_Targeted_PLGA_Lipid_mRNA_Nanocapsule_Array",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Transferrin_Targeted_PLGA_Lipid_mRNA_Nanocapsule_Array"

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
    assert fetched.name == "Study_354_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
