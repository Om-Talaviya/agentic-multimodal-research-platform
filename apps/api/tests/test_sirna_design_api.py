"""API integration tests for siRNA & Oligonucleotide Therapeutic Designer (Phase 98)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_sirna_design_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Optimize siRNA candidate
        payload = {
            "target_gene": "TTR",
            "target_mrna_sequence": "AUGGACAGCUACUUUCUUUGCUGCUCCUGGGCCUGCUCCUGGG",
            "custom_seed_exclusion": True,
        }
        res_post = await client.post("/api/v1/sirna-design/optimize", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "design_id" in data_post
        assert data_post["knockdown_potency_score"] > 85.0
        design_id = data_post["design_id"]

        # 2. Retrieve design details
        res_get = await client.get(f"/api/v1/sirna-design/designs/{design_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == design_id
        assert data_get["target_gene"] == "TTR"
        assert len(data_get["off_target_hits"]) > 0
        assert len(data_get["modifications"]) > 0
