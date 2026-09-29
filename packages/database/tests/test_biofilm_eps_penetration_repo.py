"""Tests for Phase 357: Autonomous Bacterial Biofilm Extracellular Polymeric Substance (EPS) Disruption & Penetration Simulator Repo."""

import pytest
from database.repositories.biofilm_eps_penetration_repo import BiofilmEpsPenetrationRepository


@pytest.mark.asyncio
async def test_biofilm_eps_penetration_repository(db_session):
    repo = BiofilmEpsPenetrationRepository(db_session)

    study = await repo.create_study(
        name="Study_357_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="biofilm-eps-penetration",
        biofilm_biomass_eradication_efficiency_pct=96.5,
        antimicrobial_diffusive_penetration_rate_um_min=42.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 357 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_357_Verification"
    assert getattr(study, "biofilm_biomass_eradication_efficiency_pct") == 96.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Pseudomonas_aeruginosa_Mucoid_Biofilm_Alginate_Lyase_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Pseudomonas_aeruginosa_Mucoid_Biofilm_Alginate_Lyase_Model"

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
    assert fetched.name == "Study_357_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
