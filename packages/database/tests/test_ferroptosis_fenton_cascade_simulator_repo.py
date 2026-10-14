"""Tests for Phase 482: Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator Repo."""

import pytest
from database.repositories.ferroptosis_fenton_cascade_simulator_repo import FerroptosisFentonCascadeSimulatorRepository


@pytest.mark.asyncio
async def test_ferroptosis_fenton_cascade_simulator_repository(db_session):
    repo = FerroptosisFentonCascadeSimulatorRepository(db_session)

    study = await repo.create_study(
        name="Study_482_Verification",
        target_specimen="GPX4-Inactivated HT-1080 Fibrosarcoma Spheroids with Labile Iron Pool Fe(II) Accumulation",
        analytical_modality="ferroptosis-fenton-cascade",
        lipid_hydroperoxide_accumulation_nmol_mg=34.2,
        labile_iron_pool_chelatable_uM=8.45,
        fenton_reaction_rate_constant_M_inv_s_inv=76.0,
        membrane_permeabilization_lysis_probability=0.945,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 482 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_482_Verification"
    assert study.lipid_hydroperoxide_accumulation_nmol_mg == 34.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Polyunsaturated_Fatty_Acid_Radical_Chain_Propagator",
        profile_category="Primary Step",
        quantitative_value=34.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Polyunsaturated_Fatty_Acid_Radical_Chain_Propagator"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="lipid_hydroperoxide_accumulation_nmol_mg",
        observed_value=34.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 34.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_482_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
