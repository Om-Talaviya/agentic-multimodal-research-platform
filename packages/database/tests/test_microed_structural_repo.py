"""
Database repository tests for Phase 166: MicroED Structural Engine.
"""

import pytest
from database.repositories.microed_structural_repo import MicroEDStructuralRepository


@pytest.mark.asyncio
async def test_microed_structural_repo_lifecycle(db_session):
    repo = MicroEDStructuralRepository(db_session)

    exp = await repo.create_experiment(
        sample_name="Bovine Trypsin Microcrystal",
        crystal_system="Orthorhombic P212121",
        electron_voltage_kv=200.0,
        total_rotation_range_degrees=120.0,
        resolution_limit_angstrom=0.85,
        completeness_percent=98.5,
        r_work=0.142,
        r_free=0.168,
    )
    assert exp.id is not None
    assert exp.sample_name == "Bovine Trypsin Microcrystal"

    frame = await repo.add_diffraction_frame(
        experiment_id=exp.id,
        frame_number=1,
        tilt_angle_degrees=-60.0,
        observed_reflections_count=480,
        mean_intensity_sigma_ratio=15.2,
    )
    assert frame.id is not None
    assert frame.frame_number == 1

    ref = await repo.add_refinement(
        experiment_id=exp.id,
        refinement_cycle=1,
        ramachandran_favored_percent=98.4,
        clashscore=1.1,
        electrostatic_potential_peak_density=18.6,
    )
    assert ref.id is not None
    assert ref.refinement_cycle == 1

    fetched = await repo.get_experiment(exp.id)
    assert fetched is not None
    assert len(fetched.frames) == 1
    assert len(fetched.refinements) == 1
