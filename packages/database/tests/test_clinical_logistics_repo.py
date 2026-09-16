"""
Tests for Phase 63: Clinical Trial Logistics Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.clinical_logistics_repo import ClinicalTrialLogisticsRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_clinical_logistics_repo_crud(async_session: AsyncSession):
    repo = ClinicalTrialLogisticsRepository(async_session)

    # 1. Create Network
    net = await repo.create_network(
        trial_protocol_number="PROTO-001",
        trial_title="Phase III Oncology Trial",
    )
    assert net.id is not None

    # 2. Add Sites & Routes
    updated = await repo.add_sites_and_routes(
        network_id=net.id,
        sites_data=[
            {"site_name": "Site A", "country_code": "US", "current_inventory_vials": 50}
        ],
        routes_data=[
            {"origin_depot": "Depot 1", "destination_site": "Site A", "transit_time_hours": 12.0}
        ],
        global_risk=0.15,
    )
    assert updated is not None
    assert updated.total_sites == 1
    assert len(updated.sites) == 1
    assert len(updated.routes) == 1
