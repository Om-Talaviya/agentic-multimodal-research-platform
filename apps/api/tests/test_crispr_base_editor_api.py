"""
API integration tests for Phase 164: CRISPR Base Editor.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_crispr_base_editor_api_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Predict editing profile
        payload = {
            "target_gene": "PCSK9_Exon1",
            "protospacer_sequence": "GAACACCCAGAGCCCGGACG",
            "editor_type": "ABE8e",
            "pam": "NGG",
        }
        res_post = await client.post(
            "/api/v1/crispr-base-editor/predict",
            json=payload,
            headers=auth_headers,
        )
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "study_id" in data_post
        study_id = data_post["study_id"]
        assert data_post["target_gene"] == "PCSK9_Exon1"
        assert data_post["on_target_conversion_efficiency"] > 0

        # 2. Get study
        res_get = await client.get(
            f"/api/v1/crispr-base-editor/studies/{study_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["target_gene"] == "PCSK9_Exon1"
        assert "transitions_count" in data_get
