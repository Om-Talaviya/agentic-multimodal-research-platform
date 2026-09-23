import pytest
from database.repositories.spatial_gnn_neighborhood_repo import SpatialGNNNeighborhoodRepository


@pytest.mark.asyncio
async def test_spatial_gnn_neighborhood_repo_lifecycle(db_session):
    repo = SpatialGNNNeighborhoodRepository(db_session)

    nb = await repo.create_neighborhood(
        dataset_name="10x_Xenium_Breast_InSitu",
        tissue_type="Triple Negative Breast Cancer",
        total_single_cells_indexed=52000,
        graph_connectivity_radius_um=45.0,
        gnn_embedding_dimension=128,
        spatial_homophily_ratio=0.72,
    )

    assert nb.id is not None
    assert nb.dataset_name == "10x_Xenium_Breast_InSitu"

    edge = await repo.add_proximity_graph(
        neighborhood_id=nb.id,
        source_cell_type="CD8+ T Effector",
        target_cell_type="Cytokeratin+ Tumor Epithelium",
        interaction_frequency=1240,
        spatial_enrichment_z_score=4.85,
        ligand_receptor_potential_score=0.82,
    )
    assert edge.source_cell_type == "CD8+ T Effector"

    niche = await repo.add_microdomain_niche(
        neighborhood_id=nb.id,
        niche_cluster_id="Niche_TLS_01",
        dominant_cell_composition="B-cell / T-cell Follicular Zone",
        mean_distance_to_vasculature_um=28.5,
        hypoxia_signature_enrichment=1.2,
    )
    assert niche.niche_cluster_id == "Niche_TLS_01"

    retrieved = await repo.get_neighborhood(nb.id)
    assert retrieved is not None
    assert len(retrieved.proximity_graphs) == 1
    assert len(retrieved.microdomain_niches) == 1
