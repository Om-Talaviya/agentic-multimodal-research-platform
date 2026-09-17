"""Tests for Chemogenomics Polypharmacology API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.api.main import app


@pytest.mark.asyncio
async def test_chemogenomics_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Screen Compound
        payload = {
            "compound_name": "Imatinib",
            "smiles": "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5",
            "primary_target": "ABL1",
            "affinities": [
                {
                    "target_gene": "ABL1",
                    "uniprot_id": "P00519",
                    "protein_family": "KINASE",
                    "affinity_type": "IC50",
                    "affinity_value_nm": 38.0,
                    "is_primary_target": True
                },
                {
                    "target_gene": "KIT",
                    "uniprot_id": "P10721",
                    "protein_family": "KINASE",
                    "affinity_type": "IC50",
                    "affinity_value_nm": 110.0,
                    "is_primary_target": False
                }
            ]
        }
        res = await client.post("/api/v1/chemogenomics/profiles/screen", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["compound_name"] == "Imatinib"
        assert len(data["affinities"]) == 2
        profile_id = data["id"]

        # 2. List Profiles
        res_list = await client.get("/api/v1/chemogenomics/profiles", headers=auth_headers)
        assert res_list.status_code == 200
        profiles = res_list.json()
        assert len(profiles) >= 1

        # 3. Get Profile Details
        res_get = await client.get(f"/api/v1/chemogenomics/profiles/{profile_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == profile_id
        assert details["primary_target"] == "ABL1"
        assert len(details["affinities"]) == 2
