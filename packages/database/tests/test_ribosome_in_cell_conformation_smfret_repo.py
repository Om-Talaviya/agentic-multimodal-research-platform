"""Tests for Phase 505: Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine Repo."""

import pytest
from database.repositories.ribosome_in_cell_conformation_smfret_repo import RibosomeInCellConformationSmfretRepository


@pytest.mark.asyncio
async def test_ribosome_in_cell_conformation_smfret_repository(db_session):
    repo = RibosomeInCellConformationSmfretRepository(db_session)

    study = await repo.create_study(
        name="Study_505_Verification",
        target_specimen="Intact Vitrified E. coli Cell with Dual-Fluorophore Cy3/Cy5 L11-Stalk Ribosomal Probes",
        analytical_modality="in-cell-smfret-ribosome",
        intersubunit_rotation_fret_efficiency=0.785,
        translation_elongation_cycle_rate_s_inv=18.2,
        crowding_induced_stalk_fluctuation_std=0.045,
        intact_cell_fluorophore_photobleaching_lifetime_s=42.0,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 505 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_505_Verification"
    assert study.intersubunit_rotation_fret_efficiency == 0.785

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Intersubunit_Ribosomal_Translocation_FRET_Step",
        profile_category="Primary Step",
        quantitative_value=0.785,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Intersubunit_Ribosomal_Translocation_FRET_Step"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="intersubunit_rotation_fret_efficiency",
        observed_value=0.785,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.785

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_505_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
