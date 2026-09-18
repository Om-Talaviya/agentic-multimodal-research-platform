"""API integration tests for High-Content Phenotypic Screening."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_phenotypic_screening_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get MoA signatures
        res_sig = await client.get("/api/v1/phenotypic-screening/signatures", headers=auth_headers)
        assert res_sig.status_code == 200
        data_sig = res_sig.json()
        assert "signatures" in data_sig

        # 2. Screen plate
        payload = {
            "plate_name": "Screen_Batch_009",
            "format": "384-well",
            "cell_line": "U2OS",
            "imaging_magnification": "20x",
            "wells": [
                {
                    "well_position": "B02",
                    "compound_name": "Paclitaxel",
                    "concentration_uM": 10.0,
                    "is_control": False,
                },
                {
                    "well_position": "A01",
                    "compound_name": "DMSO",
                    "concentration_uM": 0.1,
                    "is_control": True,
                },
            ],
        }
        res_post = await client.post("/api/v1/phenotypic-screening/plates", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "success"
        assert "plate_id" in data_post
        assert data_post["wells_processed"] == 2
        plate_id = data_post["plate_id"]

        # 3. Retrieve plate details
        res_get = await client.get(f"/api/v1/phenotypic-screening/plates/{plate_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == plate_id
        assert data_get["wells_count"] == 2
