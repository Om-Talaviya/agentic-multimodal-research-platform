import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from apps.api.src.api.main import app

@pytest.mark.asyncio
async def test_synthetic_lethality_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Run SL Screen
        payload = {
            "screen_name": "BRCA1 Synthetic Lethality API Screen",
            "primary_target_gene": "BRCA1",
            "tumor_indication": "Ovarian Carcinoma",
            "ceres_dependency_threshold": -0.5,
            "sample_cell_lines_count": 5
        }
        res = await client.post("/api/v1/synthetic-lethality/screen", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "screen_id" in data
        assert len(data["partners"]) >= 1
        screen_id = data["screen_id"]

        # 2. List Screens
        res_list = await client.get("/api/v1/synthetic-lethality/screens", headers=auth_headers)
        assert res_list.status_code == 200
        screens = res_list.json()
        assert len(screens) >= 1

        # 3. Get Single Screen
        res_get = await client.get(f"/api/v1/synthetic-lethality/screens/{screen_id}", headers=auth_headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == screen_id
        assert len(detail["partners"]) >= 1
        assert len(detail["dependency_scores"]) == 5
