"""Tests for Phase 304: Autonomous Multi-Omics Microbially-Derived Metabolite Host GPCR Signal Transduction & Immunomodulation Modeler Repo."""

import pytest
from database.repositories.microbial_metabolite_gpcr_signaling_repo import MicrobialMetaboliteGpcrSignalingRepository


@pytest.mark.asyncio
async def test_microbial_metabolite_gpcr_signaling_repository(db_session):
    repo = MicrobialMetaboliteGpcrSignalingRepository(db_session)

    study = await repo.create_study(
        name="Study_304_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microbial-metabolite-gpcr-signaling",
        host_gpcr_activation_potency_ec50_uM=8.4,
        treg_polarization_induction_fold=4.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 304 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_304_Verification"
    assert getattr(study, "host_gpcr_activation_potency_ec50_uM") == 8.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Butyrate_Propionate_GPR41_43_Treg_Differentiation",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Butyrate_Propionate_GPR41_43_Treg_Differentiation"

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
    assert fetched.name == "Study_304_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
