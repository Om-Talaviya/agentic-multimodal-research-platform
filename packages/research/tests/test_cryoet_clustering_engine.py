import pytest
from research.structural.cryoet_clustering_engine import (
    CryoETDeepClusteringEngine,
    SubtomogramInput,
)


def test_cryoet_deep_clustering_engine_default():
    engine = CryoETDeepClusteringEngine()
    result = engine.process_subtomogram_clustering(
        study_name="HeLa In-Situ Lamella Study",
        cellular_organism="Homo sapiens",
    )

    assert result.study_name == "HeLa In-Situ Lamella Study"
    assert result.cellular_organism == "Homo sapiens"
    assert result.total_volumes_processed == 4
    assert len(result.clusters) == 3
    assert result.clusters[0]["macromolecule_identity"] == "Eukaryotic 80S Ribosome"
    assert result.mean_resolution_angstrom > 0
    assert len(result.fsc_curves) > 0
    assert result.summary_metrics["deep_embedding_silhouette_score"] == 0.84


def test_cryoet_deep_clustering_engine_custom():
    engine = CryoETDeepClusteringEngine()
    custom_subtomos = [
        SubtomogramInput(volume_tag="Box_A", tomogram_id="Tomo_X", coord_x=10.0, coord_y=20.0, coord_z=30.0, contrast_snr=2.5),
        SubtomogramInput(volume_tag="Box_B", tomogram_id="Tomo_Y", coord_x=40.0, coord_y=50.0, coord_z=60.0, contrast_snr=2.2),
    ]
    result = engine.process_subtomogram_clustering(
        study_name="Chlamydomonas Pyrenoid",
        cellular_organism="Chlamydomonas reinhardtii",
        subtomograms=custom_subtomos,
        target_cluster_count=2,
    )

    assert result.total_volumes_processed == 2
    assert len(result.clusters) == 2
    assert len(result.representative_subtomograms) == 2
