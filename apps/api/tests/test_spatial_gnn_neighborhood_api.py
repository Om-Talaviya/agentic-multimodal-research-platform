"""API integration tests for Spatial Multi-Omics GNN Neighborhood Engine (Phase 139)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_spatial_gnn_neighborhood_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Build spatial GNN matrix
        payload = {
            "dataset_name": "Vizgen_MERSCOPE_Melanoma",
            "tissue_type": "Metastatic Cutaneous Melanoma",
            "radius_um": 50.0,
            "embedding_dim": 128,
        }
        res_post = await client.post("/api/v1/spatial-gnn/build-matrix", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "neighborhood_id" in data_post
        assert data_post["dataset_name"] == "Vizgen_MERSCOPE_Melanoma"
        assert data_post["total_cells"] > 0
        neighborhood_id = data_post["neighborhood_id"]

        # 2. Retrieve neighborhood details
        res_get = await client.get(f"/api/v1/spatial-gnn/neighborhoods/{neighborhood_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == neighborhood_id
        assert data_get["dataset_name"] == "Vizgen_MERSCOPE_Melanoma"
        assert data_get["proximity_graphs_count"] == 3
        assert data_get["microdomain_niches_count"] == 3
