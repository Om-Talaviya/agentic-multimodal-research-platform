"""API integration tests for Clinical Genomics Twin endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_clinical_twin_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get KB
        res_kb = await client.get("/api/v1/clinical-twin/guidelines-kb", headers=auth_headers)
        assert res_kb.status_code == 200
        assert "knowledge_base" in res_kb.json()

        # 2. Evaluate Clinical Twin
        payload = {
            "patient_mrn": "MRN-API-7734",
            "age": 55,
            "sex": "FEMALE",
            "ancestry": "EUROPEAN",
            "diplotypes": {
                "CYP2C19": "*2/*2",
                "CYP2D6": "*1/*4",
            },
            "target_drug": "Clopidogrel",
            "prescribed_dose_mg": 75.0,
        }
        res_ev = await client.post("/api/v1/clinical-twin/evaluate", json=payload, headers=auth_headers)
        assert res_ev.status_code == 201
        data_ev = res_ev.json()
        assert data_ev["status"] == "success"
        assert "id" in data_ev
        profile_id = data_ev["id"]
        assert data_ev["high_risk_drug_interactions_count"] == 1
        assert data_ev["guidelines_count"] == 2
        assert data_ev["simulations_count"] == 1

        # 3. List profiles
        res_list = await client.get("/api/v1/clinical-twin/profiles", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(p["id"] == profile_id for p in list_data)

        # 4. Get profile details
        res_get = await client.get(f"/api/v1/clinical-twin/profiles/{profile_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == profile_id
        assert get_data["patient_mrn"] == "MRN-API-7734"
        assert len(get_data["guidelines"]) == 2
        assert len(get_data["twin_simulations"]) == 1
