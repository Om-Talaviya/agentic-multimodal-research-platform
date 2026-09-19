"""API integration tests for Literature Discrepancy & Fact-Checking (Phase 103)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_literature_factcheck_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Run literature claim verification
        payload = {
            "paper_title": "Targeting oncogenic KRAS G12D with novel quinazoline derivatives",
            "doi_or_pmid": "10.1016/j.ejmech.2024.116234",
            "abstract_or_text": "We report the design and synthesis of potent non-covalent inhibitors of KRAS G12D.",
        }
        res_post = await client.post("/api/v1/literature-factcheck/verify", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "factcheck_id" in data_post
        assert data_post["overall_truthfulness_score"] > 80.0
        fc_id = data_post["factcheck_id"]

        # 2. Retrieve factcheck details
        res_get = await client.get(f"/api/v1/literature-factcheck/factchecks/{fc_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == fc_id
        assert data_get["paper_title"] == "Targeting oncogenic KRAS G12D with novel quinazoline derivatives"
        assert len(data_get["claims"]) > 0
        assert len(data_get["citations"]) > 0
