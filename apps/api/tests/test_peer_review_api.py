"""
Integration tests for Scientific Peer-Review REST API (Phase 64).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_peer_review_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Submit Manuscript
        res = await client.post(
            "/api/v1/peer-review/manuscripts",
            json={
                "manuscript_title": "AI Discovery Test Paper",
                "research_domain": "Immunology",
                "abstract_text": "We discover new vaccines.",
            },
        )
        assert res.status_code == 201
        data = res.json()
        m_id = data["id"]
        assert len(data["reviews"]) == 3

        # 2. Get Manuscript Detail
        get_res = await client.get(f"/api/v1/peer-review/manuscripts/{m_id}")
        assert get_res.status_code == 200
        assert get_res.json()["manuscript_title"] == "AI Discovery Test Paper"

        # 3. List Manuscripts
        list_res = await client.get("/api/v1/peer-review/manuscripts")
        assert list_res.status_code == 200
        assert any(m["id"] == m_id for m in list_res.json())
