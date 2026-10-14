"""Tests for Phase 507: Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator Repo."""

import pytest
from database.repositories.metabolic_retrosynthesis_xenobiology_repo import MetabolicRetrosynthesisXenobiologyRepository


@pytest.mark.asyncio
async def test_metabolic_retrosynthesis_xenobiology_repository(db_session):
    repo = MetabolicRetrosynthesisXenobiologyRepository(db_session)

    study = await repo.create_study(
        name="Study_507_Verification",
        target_specimen="In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes",
        analytical_modality="xenobiotic-retrosynthesis-flux",
        retrosynthetic_pathway_plausibility_score=0.942,
        thermodynamic_driving_force_delta_G_kj_mol=-34.8,
        theoretical_maximum_carbon_yield_pct=92.5,
        chassis_endogenous_flux_perturbation_index=0.125,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 507 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_507_Verification"
    assert study.retrosynthetic_pathway_plausibility_score == 0.942

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="De_Novo_Enzymatic_Cascade_Thermodynamic_Feasibility",
        profile_category="Primary Step",
        quantitative_value=0.942,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "De_Novo_Enzymatic_Cascade_Thermodynamic_Feasibility"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="retrosynthetic_pathway_plausibility_score",
        observed_value=0.942,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.942

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_507_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
