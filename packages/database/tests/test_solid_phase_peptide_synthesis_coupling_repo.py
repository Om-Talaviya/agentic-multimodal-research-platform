"""Tests for Phase 445: Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine Repo."""

import pytest
from database.repositories.solid_phase_peptide_synthesis_coupling_repo import SolidPhasePeptideSynthesisRepository


@pytest.mark.asyncio
async def test_solid_phase_peptide_synthesis_coupling_repository(db_session):
    repo = SolidPhasePeptideSynthesisRepository(db_session)

    study = await repo.create_study(
        name="Study_445_Verification",
        target_specimen="40-Mer Hydrophobic Amyloid-Beta Peptide Intermediate on Wang Resin Microbeads",
        analytical_modality="solid-phase-peptide-synthesis",
        fmoc_deprotection_efficiency_ratio=0.994,
        coupling_reaction_half_life_seconds=45.2,
        aggregation_beta_sheet_propensity=0.285,
        purity_crude_hplc_percentage=94.6,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 445 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_445_Verification"
    assert study.fmoc_deprotection_efficiency_ratio == 0.994

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Fmoc_Cleavage_Piperidine_Deprotection_Peak",
        profile_category="Primary Step",
        quantitative_value=0.994,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Fmoc_Cleavage_Piperidine_Deprotection_Peak"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fmoc_deprotection_efficiency_ratio",
        observed_value=0.994,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.994

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_445_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
