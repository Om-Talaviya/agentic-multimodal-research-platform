"""Tests for Clinical Site Selection API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_clinical_site_selection_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Evaluate & Create Study
        payload = {
            "study_title": "Global Phase 3 NSCLC Trial",
            "protocol_code": "NSCLC-303",
            "indication": "Non-Small Cell Lung Cancer",
            "phase": "Phase 3",
            "target_enrollment": 300,
            "recruitment_duration_months": 14.0,
            "dropout_rate": 0.10,
            "sites": [
                {
                    "site_name": "Memorial Oncology Center",
                    "country": "United States",
                    "city": "New York",
                    "principal_investigator": "Dr. Sarah Lin",
                    "historical_recruitment_rate": 3.2,
                    "ethics_approval_timeline_days": 35,
                    "patient_pool_density": 4500,
                    "pi_experience_years": 10.0,
                    "competing_trials_count": 1
                },
                {
                    "site_name": "St. Jude Research Hospital",
                    "country": "United Kingdom",
                    "city": "London",
                    "principal_investigator": "Dr. Alistair Vance",
                    "historical_recruitment_rate": 2.0,
                    "ethics_approval_timeline_days": 50,
                    "patient_pool_density": 2500,
                    "pi_experience_years": 7.0,
                    "competing_trials_count": 2
                }
            ]
        }
        res = await client.post("/api/v1/clinical-sites/studies/evaluate", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["protocol_code"] == "NSCLC-303"
        assert len(data["sites"]) == 2
        assert "simulation" in data
        study_id = data["id"]

        # 2. List Studies
        res_list = await client.get("/api/v1/clinical-sites/studies", headers=auth_headers)
        assert res_list.status_code == 200
        studies = res_list.json()
        assert len(studies) >= 1

        # 3. Get Study Details
        res_get = await client.get(f"/api/v1/clinical-sites/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == study_id
        assert len(details["sites"]) == 2
        assert len(details["simulations"]) >= 1

        # 4. Run Additional Simulation
        sim_payload = {
            "simulation_name": "Fast-Track Acceleration Simulation",
            "dropout_rate": 0.08,
            "n_simulations": 50
        }
        res_sim = await client.post(f"/api/v1/clinical-sites/studies/{study_id}/simulate", json=sim_payload, headers=auth_headers)
        assert res_sim.status_code == 200
        sim_data = res_sim.json()
        assert "id" in sim_data
        assert sim_data["p50_completion_months"] > 0
