"""Integration tests for Epigenetic CRISPR API (Phase 159)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_crispr_epigenetic_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "target_locus_name": "API-B2M-Locus",
            "catalytic_effector": "dCas9-DNMT3A-DNMT3L",
            "guide_rna_sequence": "GGCUAGCGUAGCUAGCUAGC",
            "target_cpg_count": 10,
        }
        res = await client.post("/api/v1/crispr-epigenetic/edit", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["target_locus_name"] == "API-B2M-Locus"
        assert len(data["cpg_profiles"]) >= 4
        assert len(data["off_targets"]) >= 2
