"""
Database repository tests for Phase 165: PDC Conjugate.
"""

import pytest
from database.repositories.pdc_conjugate_repo import PDCConjugateRepository


@pytest.mark.asyncio
async def test_pdc_conjugate_repo_lifecycle(db_session):
    repo = PDCConjugateRepository(db_session)

    study = await repo.create_study(
        pdc_name="cRGD-ValCit-MMAE",
        homing_peptide_sequence="cyclo(RGDfK)",
        linker_type="Val-Cit-PABC",
        cytotoxic_payload="Monomethyl Auristatin E (MMAE)",
        plasma_stability_half_life_hours=96.0,
        tumor_cathepsin_cleavage_rate_kcat_km=48000.0,
        therapeutic_index_ratio=44.1,
    )
    assert study.id is not None
    assert study.pdc_name == "cRGD-ValCit-MMAE"

    cp = await repo.add_cleavage_profile(
        study_id=study.id,
        enzyme_target="Cathepsin-B",
        cleavage_efficiency_percent=94.5,
        incubation_time_minutes=60.0,
        intact_conjugate_remaining_percent=5.5,
    )
    assert cp.id is not None
    assert cp.cleavage_efficiency_percent == 94.5

    ca = await repo.add_cathepsin_assay(
        study_id=study.id,
        tissue_compartment="Tumor Interstitial Stroma",
        enzymatic_activity_units=142.0,
        payload_release_velocity_nmol_min=18.4,
        selectivity_fold_enrichment=24.5,
    )
    assert ca.id is not None
    assert ca.selectivity_fold_enrichment == 24.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert len(fetched.cleavage_profiles) == 1
    assert len(fetched.cathepsin_assays) == 1
