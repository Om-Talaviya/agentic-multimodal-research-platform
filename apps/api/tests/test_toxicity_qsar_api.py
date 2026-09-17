import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_toxicity_qsar_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Screen Toxicity
        payload = {
            "compound_name": "API-Candidate-Tox-99",
            "smiles_string": "Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C",
            "molecular_weight": 493.6,
            "log_p": 3.2
        }
        res = await client.post("/api/v1/toxicity-qsar/screen", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "screen_id" in data
        assert data["ames_mutagenicity_status"] in ["POSITIVE", "NEGATIVE"]
        screen_id = data["screen_id"]

        # 2. List Screens
        res_list = await client.get("/api/v1/toxicity-qsar/screens", headers=auth_headers)
        assert res_list.status_code == 200
        screens = res_list.json()
        assert len(screens) >= 1

        # 3. Get Single Screen
        res_get = await client.get(f"/api/v1/toxicity-qsar/screens/{screen_id}", headers=auth_headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == screen_id
