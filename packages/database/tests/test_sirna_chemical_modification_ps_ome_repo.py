"""Tests for Phase 230: Autonomous siRNA Phosphorothioate & 2-O-Methyl Stability Optimization Engine Repo."""

import pytest
from database.repositories.sirna_chemical_modification_ps_ome_repo import SirnaChemicalModificationPsOmeRepository


@pytest.mark.asyncio
async def test_sirna_chemical_modification_ps_ome_repository(db_session):
    repo = SirnaChemicalModificationPsOmeRepository(db_session)

    study = await repo.create_study(
        name="Study_230_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="sirna-chemical-modification-ps-ome",
        serum_half_life_exonuclease_hours=94.5,
        tlr7_8_immune_quiescence_pct=99.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 230 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_230_Verification"
    assert getattr(study, "serum_half_life_exonuclease_hours") == 94.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="PCSK9_Targeting_Enhanced_Stability_siRNA_v4",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "PCSK9_Targeting_Enhanced_Stability_siRNA_v4"

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
    assert fetched.name == "Study_230_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
