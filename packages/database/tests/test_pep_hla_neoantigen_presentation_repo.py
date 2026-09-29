"""Tests for Phase 278: Autonomous De-Novo Peptide-HLA Class I Neoantigen Presentation & TCR Repertoire Cross-Reactivity Predictor Repo."""

import pytest
from database.repositories.pep_hla_neoantigen_presentation_repo import PepHlaNeoantigenPresentationRepository


@pytest.mark.asyncio
async def test_pep_hla_neoantigen_presentation_repository(db_session):
    repo = PepHlaNeoantigenPresentationRepository(db_session)

    study = await repo.create_study(
        name="Study_278_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="pep-hla-neoantigen-presentation",
        neoantigen_surface_presentation_probability=95.8,
        tcr_cross_reactive_self_similarity_penalty=0.08,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 278 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_278_Verification"
    assert getattr(study, "neoantigen_surface_presentation_probability") == 95.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Melanoma_BRAF_V600E_HLA_A0201_Neoantigen_Complex",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Melanoma_BRAF_V600E_HLA_A0201_Neoantigen_Complex"

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
    assert fetched.name == "Study_278_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
