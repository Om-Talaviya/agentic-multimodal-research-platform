"""
Tests for Phase 59: ADC Design Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.adc_design_repo import ADCDesignRepository


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
async def test_adc_repo_crud(async_session: AsyncSession):
    repo = ADCDesignRepository(async_session)

    # 1. Create Campaign
    camp = await repo.create_campaign(
        antibody_name="Trastuzumab",
        target_antigen="HER2",
        target_dar=8.0,
    )
    assert camp.id is not None

    # 2. Add Constructs
    constructs = await repo.add_constructs(
        campaign_id=camp.id,
        constructs_data=[
            {
                "construct_code": "TRA-DXD-01",
                "payload_name": "DXd",
                "payload_class": "Topoisomerase I",
                "linker_type": "GGFG Cleavable",
                "measured_dar": 7.8,
                "therapeutic_index_score": 9.4,
                "recommended_lead": True,
            }
        ],
    )
    assert len(constructs) == 1

    # 3. Get Campaign
    fetched = await repo.get_campaign(camp.id)
    assert fetched is not None
    assert fetched.total_constructs_screened == 1
    assert len(fetched.constructs) == 1
