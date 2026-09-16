import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app
from database.connection import get_db_session, Base

@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()

@pytest.mark.asyncio
async def test_cart_api_full_flow(client: AsyncClient):
    res = await client.post("/api/v1/cart/constructs", json={
        "construct_name": "CAR-T-BCMA-41BB",
        "target_antigen": "BCMA",
        "scfv_binder_clone": "11D5-3",
        "costimulatory_domain": "4-1BB"
    })
    assert res.status_code == 201
    construct_id = res.json()["id"]

    sim_res = await client.post(f"/api/v1/cart/constructs/{construct_id}/simulate-cytotoxicity", json={
        "target_cell_line": "MM.1S",
        "effector_to_target_ratio": 10.0
    })
    assert sim_res.status_code == 200
    assert sim_res.json()["specific_lysis_pct"] > 70.0

    crs_res = await client.post(f"/api/v1/cart/constructs/{construct_id}/predict-crs", json={
        "tumor_burden_index": 1.5
    })
    assert crs_res.status_code == 200
    assert "astct_crs_grade_predicted" in crs_res.json()
