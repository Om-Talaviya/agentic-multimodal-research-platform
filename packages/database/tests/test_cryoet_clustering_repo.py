"""Tests for Phase 133 CryoETClusteringRepository."""

import pytest
from database.repositories.cryoet_clustering_repo import CryoETClusteringRepository


@pytest.mark.asyncio
async def test_cryoet_clustering_repo_lifecycle(db_session):
    repo = CryoETClusteringRepository(db_session)

    # 1. Create study
    study = await repo.create_study(
        study_name="Chlamydomonas_InSitu_Ribosome_Tomography",
        cellular_organism="Chlamydomonas reinhardtii",
        tilt_series_count=60,
        total_subtomograms_extracted=18400,
        voxel_size_angstrom=1.28,
        mean_resolution_angstrom=2.95,
        metadata_json={"microscope": "Titan Krios G4", "detector": "K3 BioQuantum"},
    )
    assert study.id is not None
    assert study.study_name == "Chlamydomonas_InSitu_Ribosome_Tomography"
    assert study.tilt_series_count == 60

    # 2. Add volume
    vol = await repo.add_volume(
        study_id=study.id,
        volume_tag="Subtomo_Box_00142",
        tomogram_id="Tomo_Cell04_Lamella02",
        coord_x=1420.5,
        coord_y=2840.1,
        coord_z=310.8,
        signal_to_noise_ratio=2.15,
        cross_correlation_score=0.89,
        assigned_cluster="Cluster_80S_Translating",
    )
    assert vol.id is not None
    assert vol.coord_x == 1420.5

    # 3. Add cluster
    cluster = await repo.add_cluster(
        study_id=study.id,
        cluster_label="Cluster_80S_Translating",
        macromolecule_identity="Cytosolic 80S Ribosome",
        particle_count=4820,
        fsc_resolution_angstrom=2.85,
        b_factor_sharpening=-75.0,
        conformational_state="Polysome Engaged State",
    )
    assert cluster.id is not None
    assert cluster.macromolecule_identity == "Cytosolic 80S Ribosome"

    # 4. Fetch study
    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert len(fetched.volumes) == 1
    assert len(fetched.clusters) == 1
    assert fetched.mean_resolution_angstrom == 2.95

    # 5. List studies
    studies = await repo.list_studies(limit=10)
    assert len(studies) >= 1
