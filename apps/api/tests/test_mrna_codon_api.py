"""Integration tests for mRNA Codon API (Phase 153)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_mrna_codon_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "target_protein_name": "API-Spike-Antigen",
            "expression_host": "Homo sapiens",
            "amino_acid_sequence": "MFVFLVLLPLVSSQCVNLTTRTQLPPAYTN",
            "target_gc_percent": 58.0,
        }
        res = await client.post("/api/v1/mrna-codon/optimize", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["target_protein_name"] == "API-Spike-Antigen"
        assert len(data["candidate_variants"]) == 3
        assert len(data["cai_profile_sample"]) == 5
