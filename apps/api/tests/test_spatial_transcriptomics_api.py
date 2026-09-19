"""API integration tests for Spatial Transcriptomics & TME Cellular Deconvolution."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_spatial_transcriptomics_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get reference signatures
        res_sig = await client.get("/api/v1/spatial-transcriptomics/signatures", headers=auth_headers)
        assert res_sig.status_code == 200
        data_sig = res_sig.json()
        assert "signatures" in data_sig
        assert "CD8_T_Cell" in data_sig["signatures"]

        # 2. Analyze spatial slice
        payload = {
            "sample_name": "HER2_Breast_Tissue_Section_01",
            "tissue_type": "HER2+ Invasive Ductal Carcinoma",
            "platform": "10x Visium HD",
            "total_spots": 4992,
        }
        res_post = await client.post("/api/v1/spatial-transcriptomics/analyze", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "slice_id" in data_post
        assert "spatial_entropy_score" in data_post
        slice_id = data_post["slice_id"]

        # 3. Retrieve slice details
        res_get = await client.get(f"/api/v1/spatial-transcriptomics/slice/{slice_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == slice_id
        assert data_get["sample_name"] == "HER2_Breast_Tissue_Section_01"
        assert len(data_get["cell_proportions"]) > 0
        assert len(data_get["ligand_receptors"]) > 0
