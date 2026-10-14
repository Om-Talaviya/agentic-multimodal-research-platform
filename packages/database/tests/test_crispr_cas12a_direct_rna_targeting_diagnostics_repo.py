"""Tests for Phase 525: Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine Repo."""

import pytest
from database.repositories.crispr_cas12a_direct_rna_targeting_diagnostics_repo import CrisprCas12aDirectRnaTargetingDiagnosticsRepository


@pytest.mark.asyncio
async def test_crispr_cas12a_direct_rna_targeting_diagnostics_repository(db_session):
    repo = CrisprCas12aDirectRnaTargetingDiagnosticsRepository(db_session)

    study = await repo.create_study(
        name="Study_525_Verification",
        target_specimen="Engineered Dual-Domain Acidaminococcus sp. Cas12a Variant bound to Synthetic SARS-CoV-3 RNA Target",
        analytical_modality="cas12a-direct-rna-cleavage",
        collateral_ssdna_probe_turnover_rate_s_inv=240.0,
        single_nucleotide_variant_specificity_ratio=85.0,
        limit_of_detection_attomolar_aM=15.0,
        isothermal_reaction_kinetic_delay_time_min=12.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 525 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_525_Verification"
    assert study.collateral_ssdna_probe_turnover_rate_s_inv == 240.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="RNA_Target_Activated_Non_Specific_Fluorophore_Quencher_Release",
        profile_category="Primary Step",
        quantitative_value=240.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "RNA_Target_Activated_Non_Specific_Fluorophore_Quencher_Release"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="collateral_ssdna_probe_turnover_rate_s_inv",
        observed_value=240.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 240.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_525_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
