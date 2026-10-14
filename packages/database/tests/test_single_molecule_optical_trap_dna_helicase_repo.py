"""Tests for Phase 512: Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper Repo."""

import pytest
from database.repositories.single_molecule_optical_trap_dna_helicase_repo import SingleMoleculeOpticalTrapDnaHelicaseRepository


@pytest.mark.asyncio
async def test_single_molecule_optical_trap_dna_helicase_repository(db_session):
    repo = SingleMoleculeOpticalTrapDnaHelicaseRepository(db_session)

    study = await repo.create_study(
        name="Study_512_Verification",
        target_specimen="Dual-Beam Optical Trap Tethered dsDNA Hairpin with Recombinant Human Bloom Syndrome Helicase",
        analytical_modality="optical-trap-helicase-unwinding",
        helicase_stepping_velocity_bp_per_s=48.5,
        atp_fuel_efficiency_bp_per_atp=1.0,
        strand_unwinding_processivity_bp=1450.0,
        sub_nanometer_step_size_bp=1.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 512 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_512_Verification"
    assert study.helicase_stepping_velocity_bp_per_s == 48.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="dsDNA_Hairpin_Force_Unzipping_Displacement",
        profile_category="Primary Step",
        quantitative_value=48.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "dsDNA_Hairpin_Force_Unzipping_Displacement"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="helicase_stepping_velocity_bp_per_s",
        observed_value=48.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 48.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_512_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
