"""Tests for Phase 515: Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter Repo."""

import pytest
from database.repositories.epigenetic_crispr_chromatin_loop_extrusion_repo import EpigeneticCrisprChromatinLoopExtrusionRepository


@pytest.mark.asyncio
async def test_epigenetic_crispr_chromatin_loop_extrusion_repository(db_session):
    repo = EpigeneticCrisprChromatinLoopExtrusionRepository(db_session)

    study = await repo.create_study(
        name="Study_515_Verification",
        target_specimen="Human K562 Cells with Chemically Dimerizable dCas9-CTCF Targeted to MYC Super-Enhancer TAD",
        analytical_modality="crispr-chromatin-loop-rewriting",
        induced_chromatin_loop_contact_frequency_enhancement=4.2,
        insulation_boundary_score_gain=0.825,
        target_oncogene_expression_activation_fold=5.4,
        cohesin_retention_time_at_engineered_ctcf_min=38.0,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 515 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_515_Verification"
    assert study.induced_chromatin_loop_contact_frequency_enhancement == 4.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="De_Novo_TAD_Boundary_Insulation_Formation",
        profile_category="Primary Step",
        quantitative_value=4.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "De_Novo_TAD_Boundary_Insulation_Formation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="induced_chromatin_loop_contact_frequency_enhancement",
        observed_value=4.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 4.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_515_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
