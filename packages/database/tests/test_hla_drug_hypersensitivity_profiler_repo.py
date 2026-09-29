"""Tests for Phase 346: Autonomous Pharmacogenomic HLA-Allele Drug Hypersensitivity & Adverse Reaction Profiler Repo."""

import pytest
from database.repositories.hla_drug_hypersensitivity_profiler_repo import HlaDrugHypersensitivityProfilerRepository


@pytest.mark.asyncio
async def test_hla_drug_hypersensitivity_profiler_repository(db_session):
    repo = HlaDrugHypersensitivityProfilerRepository(db_session)

    study = await repo.create_study(
        name="Study_346_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="hla-drug-hypersensitivity",
        hla_allele_adverse_hypersensitivity_risk_score=99.1,
        altered_peptide_repertoire_binding_affinity_nm=18.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 346 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_346_Verification"
    assert getattr(study, "hla_allele_adverse_hypersensitivity_risk_score") == 99.1

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Abacavir_HLA_B_5701_Antigen_Binding_Cleft_Docking_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Abacavir_HLA_B_5701_Antigen_Binding_Cleft_Docking_Model"

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
    assert fetched.name == "Study_346_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
