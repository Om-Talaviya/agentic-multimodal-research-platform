"""Tests for Cryo-ET Subtomogram Averaging Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.cryoet_subtomogram_tomography_repo import CryoETTomogramRepository


@pytest.mark.asyncio
async def test_cryoet_tomogram_repo_crud(db_session: AsyncSession) -> None:
    repo = CryoETTomogramRepository(db_session)

    study = await repo.create_study(
        study_name="Test AMPAR Cryo-ET",
        cellular_context="Neuronal Synapse",
        target_complex_name="AMPAR-TARP",
        particles_picked_count=1,
        final_fsc_resolution_angstrom=3.42,
        angular_search_step_deg=3.75,
        summary_metrics={"score": 3.42},
        particles=[
            {
                "particle_id_str": "PTCL_TOMO_001",
                "x_vox": 512.4,
                "y_vox": 384.8,
                "z_vox": 128.0,
                "euler_rot_deg": 45.2,
                "euler_tilt_deg": 32.8,
                "euler_psi_deg": 18.4,
                "cross_correlation_score": 0.885,
                "conformational_state": "Resting Closed",
            }
        ],
        classes=[
            {
                "class_number": 1,
                "class_name": "State 1: Resting Closed",
                "particle_occupancy_pct": 100.0,
                "resolution_angstrom": 3.42,
                "fsc_cutoff_type": "FSC_0.143_GoldStandard",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test AMPAR Cryo-ET"
    assert len(study.particles) == 1
    assert len(study.classes) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.cellular_context == "Neuronal Synapse"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
