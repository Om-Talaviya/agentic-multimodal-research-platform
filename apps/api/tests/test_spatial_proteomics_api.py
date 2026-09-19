"""API integration tests for Multiplexed Spatial Proteomics & IMC Analyzer (Phase 102)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_spatial_proteomics_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get marker panel
        res_panel = await client.get("/api/v1/spatial-proteomics/marker-panel", headers=auth_headers)
        assert res_panel.status_code == 200
        data_panel = res_panel.json()
        assert "markers" in data_panel
        assert len(data_panel["markers"]) > 0

        # 2. Analyze spatial proteomics slice
        payload = {
            "sample_name": "Melanoma_FFPE_Tissue_IMC_01",
            "tissue_origin": "Cutaneous Melanoma Stage III",
            "imaging_modality": "Hyperion Imaging Mass Cytometry",
            "segmented_cells": 24500,
        }
        res_post = await client.post("/api/v1/spatial-proteomics/analyze", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "experiment_id" in data_post
        assert data_post["immune_infiltration_score"] > 70.0
        exp_id = data_post["experiment_id"]

        # 3. Retrieve experiment details
        res_get = await client.get(f"/api/v1/spatial-proteomics/experiments/{exp_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == exp_id
        assert data_get["sample_name"] == "Melanoma_FFPE_Tissue_IMC_01"
        assert len(data_get["marker_channels"]) > 0
        assert len(data_get["neighborhoods"]) > 0
