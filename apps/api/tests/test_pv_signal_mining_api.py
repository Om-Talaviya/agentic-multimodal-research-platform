"""Tests for Pharmacovigilance Signal Mining API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.api.main import app


@pytest.mark.asyncio
async def test_pv_signal_mining_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Mine Study
        payload = {
            "study_name": "Post-Marketing Checkpoint Inhibitor Myocarditis",
            "drug_name": "Pembrolizumab",
            "active_substance": "Anti-PD-1 mAb",
            "target_adverse_event": "Autoimmune Myocarditis",
            "data_source": "FAERS",
            "a_count": 48,
            "b_count": 1250,
            "c_count": 110,
            "d_count": 42000
        }
        res = await client.post("/api/v1/pv-sentinel/studies/mine", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["drug_name"] == "Pembrolizumab"
        assert data["signal_status"] in ["CONFIRMED_SIGNAL", "POTENTIAL_SIGNAL"]
        assert len(data["metrics"]) >= 1
        assert len(data["case_reports"]) >= 1
        study_id = data["id"]

        # 2. List Studies
        res_list = await client.get("/api/v1/pv-sentinel/studies", headers=auth_headers)
        assert res_list.status_code == 200
        studies = res_list.json()
        assert len(studies) >= 1

        # 3. Get Study Details
        res_get = await client.get(f"/api/v1/pv-sentinel/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == study_id
        assert details["drug_name"] == "Pembrolizumab"
        assert len(details["metrics"]) >= 1
        assert len(details["case_reports"]) >= 1
