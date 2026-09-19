"""API integration tests for CRISPR Prime & Base Editing (Phase 101)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_prime_editing_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Design prime editing pegRNA
        payload = {
            "target_gene": "HBB",
            "genomic_locus": "chr11:5227002",
            "intended_edit": "POINT_MUTATION_E6V_CORRECTION",
            "editor_architecture": "PEmax_PE3",
        }
        res_post = await client.post("/api/v1/prime-editing/design", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "design_id" in data_post
        assert data_post["predicted_editing_efficiency_pct"] > 50.0
        design_id = data_post["design_id"]

        # 2. Retrieve design details
        res_get = await client.get(f"/api/v1/prime-editing/designs/{design_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == design_id
        assert data_get["target_gene"] == "HBB"
        assert len(data_get["pegrna_candidates"]) == 2
        assert len(data_get["bystander_alerts"]) == 2
