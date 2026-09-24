"""Integration tests for TCR-pMHC API (Phase 145)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_tcr_pmhc_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "tcr_name": "MART-1-TCR-DMF5",
            "cdr3_alpha_seq": "CAVNFAGGYQLIW",
            "cdr3_beta_seq": "CASSIRSSYEQYF",
            "target_peptide": "ELAGIGILTV",
            "hla_allele": "HLA-A*02:01",
        }
        res = await client.post("/api/v1/tcr-pmhc/predict", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["tcr_name"] == "MART-1-TCR-DMF5"
        assert len(data["cross_reactivity_scan"]) == 3
