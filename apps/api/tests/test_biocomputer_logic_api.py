"""
API integration tests for Phase 131: Biocomputer Gene Logic Circuits.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from api.dependencies import get_db
from main import app


@pytest.fixture
async def test_app():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_biocomputer_logic_api_flow(test_app: AsyncClient):
    payload = {
        "circuit_name": "Pancreatic_Adenocarcinoma_Classifier_v1",
        "target_cell_type": "Pancreatic Ductal Adenocarcinoma (PDAC)",
        "logic_expression": "(KRAS_G12D AND NOT miR-216) AND (MUC1 OR CEACAM5)",
        "output_payload": "Pseudomonas_Exotoxin_A",
        "biomarkers": [
            {"marker_name": "KRAS_G12D", "target_state": True, "threshold_rfu": 1500.0},
            {"marker_name": "miR-216", "target_state": False, "threshold_rfu": 500.0},
            {"marker_name": "MUC1", "target_state": True, "threshold_rfu": 2000.0},
            {"marker_name": "CEACAM5", "target_state": True, "threshold_rfu": 1800.0},
        ],
    }

    # 1. Run simulation
    res = await test_app.post("/api/v1/biocomputer-logic/simulate", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "circuit_id" in data
    circuit_id = data["circuit_id"]
    assert data["gates_count"] >= 3
    assert data["truth_table_states"] == 16
    assert data["classifier_metrics"]["classification_accuracy"] >= 0.90

    # 2. List circuits
    list_res = await test_app.get("/api/v1/biocomputer-logic/circuits")
    assert list_res.status_code == 200
    circuits = list_res.json()
    assert any(c["id"] == circuit_id for c in circuits)

    # 3. Retrieve single circuit details
    get_res = await test_app.get(f"/api/v1/biocomputer-logic/circuits/{circuit_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["circuit_name"] == "Pancreatic_Adenocarcinoma_Classifier_v1"
    assert len(detail["gates"]) >= 3
    assert len(detail["classifiers"]) == 1
    assert detail["classifiers"][0]["output_payload"] == "Pseudomonas_Exotoxin_A"
