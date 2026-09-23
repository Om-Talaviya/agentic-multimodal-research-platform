"""API integration tests for Cryo-ET Subtomogram Deep Clustering Engine (Phase 133)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_cryoet_clustering_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Process clustering
        payload = {
            "study_name": "In-Situ Neuronal Synapse Tomography",
            "cellular_organism": "Rattus norvegicus",
            "voxel_size_angstrom": 1.42,
            "target_cluster_count": 3,
            "subtomograms": [
                {
                    "volume_tag": "Synapse_Box_01",
                    "tomogram_id": "Tomo_Neur_01",
                    "coord_x": 100.0,
                    "coord_y": 250.0,
                    "coord_z": 45.0,
                    "contrast_snr": 2.2,
                },
                {
                    "volume_tag": "Synapse_Box_02",
                    "tomogram_id": "Tomo_Neur_01",
                    "coord_x": 300.0,
                    "coord_y": 550.0,
                    "coord_z": 65.0,
                    "contrast_snr": 1.8,
                },
            ],
        }
        res_post = await client.post("/api/v1/cryoet-clustering/process", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "study_id" in data_post
        assert data_post["study_name"] == "In-Situ Neuronal Synapse Tomography"
        study_id = data_post["study_id"]

        # 2. Retrieve study details
        res_get = await client.get(f"/api/v1/cryoet-clustering/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["study_name"] == "In-Situ Neuronal Synapse Tomography"
        assert data_get["volumes_count"] == 2
        assert data_get["clusters_count"] == 3
