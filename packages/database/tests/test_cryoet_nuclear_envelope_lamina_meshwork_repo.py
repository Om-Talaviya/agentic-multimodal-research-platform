"""Tests for Phase 511: Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine Repo."""

import pytest
from database.repositories.cryoet_nuclear_envelope_lamina_meshwork_repo import CryoetNuclearEnvelopeLaminaMeshworkRepository


@pytest.mark.asyncio
async def test_cryoet_nuclear_envelope_lamina_meshwork_repository(db_session):
    repo = CryoetNuclearEnvelopeLaminaMeshworkRepository(db_session)

    study = await repo.create_study(
        name="Study_511_Verification",
        target_specimen="Vitrified Fibroblast Nucleus Section with Lamin A/C Filamentous Intermediate Meshwork",
        analytical_modality="cryoet-nuclear-envelope-lamina",
        lamin_filament_diameter_nm=3.5,
        orthogonal_meshwork_pore_size_nm=48.0,
        nuclear_membrane_elastic_modulus_kPa=12.5,
        subtomogram_averaging_fsc_resolution_angstrom=6.4,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 511 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_511_Verification"
    assert study.lamin_filament_diameter_nm == 3.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Lamin_Intermediate_Filament_Meshwork_Tomogram",
        profile_category="Primary Step",
        quantitative_value=3.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Lamin_Intermediate_Filament_Meshwork_Tomogram"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="lamin_filament_diameter_nm",
        observed_value=3.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_511_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
