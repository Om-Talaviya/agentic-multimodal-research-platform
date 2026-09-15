"""Tests for SingleCellRepository."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.single_cell_repo import SingleCellRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_single_cell_repo_lifecycle(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="single_cell_biologist", email="scrna@broad.mit.edu", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = SingleCellRepository(async_session)

    # 1. Create dataset
    dataset = await repo.create_dataset(
        user_id=user_id,
        dataset_title="Human Liver LNP Uptake scRNA-seq Atlas",
        organism="Homo sapiens",
        tissue="Liver",
        sequencing_platform="10x Chromium Next GEM 3' v3.1",
        total_cells=600,
        total_genes=28450,
        clustering_resolution=0.5,
        metadata_json={"median_umi": 4850},
    )

    assert dataset.id is not None
    assert dataset.dataset_title == "Human Liver LNP Uptake scRNA-seq Atlas"

    # 2. Add clusters
    clusters = await repo.add_clusters(
        dataset_id=dataset.id,
        clusters_data=[
            {
                "cluster_index": 0,
                "cell_type_annotation": "Mature Hepatocytes",
                "cell_count": 228,
                "percentage_of_total": 38.0,
                "top_markers_json": ["ALB", "APOA1", "CYP3A4", "PCK1"],
            },
            {
                "cluster_index": 1,
                "cell_type_annotation": "LNP-Transfected Hepatocytes",
                "cell_count": 132,
                "percentage_of_total": 22.0,
                "top_markers_json": ["LDLR", "HMGCR", "SQLE", "EGFP_Reporter"],
            },
        ],
    )
    assert len(clusters) == 2

    # 3. Add cell coordinates
    coords = await repo.add_cell_coordinates(
        dataset_id=dataset.id,
        coordinates_data=[
            {
                "cell_barcode": "CELL_00_0001_8492",
                "cluster_index": 0,
                "umap_x": -3.24,
                "umap_y": 2.51,
                "tsne_x": -18.2,
                "tsne_y": 14.1,
                "pseudotime_value": 0.15,
                "cell_type_annotation": "Mature Hepatocytes",
            }
        ],
    )
    assert len(coords) == 1

    # 4. Add differential genes
    genes = await repo.add_differential_genes(
        dataset_id=dataset.id,
        genes_data=[
            {
                "cluster_index": 0,
                "gene_symbol": "ALB",
                "log2_fold_change": 4.25,
                "p_value": 1e-45,
                "p_val_adj": 1.5e-45,
                "pct_in_cluster": 0.98,
                "pct_out_of_cluster": 0.12,
                "is_significant": True,
            }
        ],
    )
    assert len(genes) == 1

    # 5. Add pathway enrichments
    pathways = await repo.add_pathway_enrichments(
        dataset_id=dataset.id,
        pathways_data=[
            {
                "cluster_index": 0,
                "pathway_name": "Fatty Acid & Lipid Metabolism",
                "database_source": "KEGG",
                "normalized_enrichment_score": 2.45,
                "p_val_adj": 1.2e-6,
                "leading_edge_genes_json": ["APOA1", "CYP3A4", "PCK1"],
            }
        ],
    )
    assert len(pathways) == 1

    # 6. Retrieve full dataset
    loaded = await repo.get_dataset(dataset.id)
    assert loaded is not None
    assert len(loaded.clusters) == 2
    assert len(loaded.differential_genes) == 1
    assert len(loaded.pathway_enrichments) == 1

    # 7. Coordinates and markers fetch
    coords_fetch = await repo.get_dataset_coordinates(dataset.id, limit=100)
    assert len(coords_fetch) == 1

    markers_fetch = await repo.get_dataset_markers(dataset.id, cluster_index=0)
    assert len(markers_fetch) == 1
    assert markers_fetch[0].gene_symbol == "ALB"

    # 8. List datasets
    ds_list = await repo.list_datasets(user_id=user_id)
    assert len(ds_list) == 1

    # 9. Delete dataset
    deleted = await repo.delete_dataset(dataset.id)
    assert deleted is True
    assert await repo.get_dataset(dataset.id) is None
