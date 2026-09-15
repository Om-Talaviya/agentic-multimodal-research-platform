"""Unit tests for Pharmacovigilance Repository (Phase 49)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.pharmacovigilance_repo import PharmacovigilanceRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_pharmacovigilance_repo_crud(async_session: AsyncSession):
    repo = PharmacovigilanceRepository(async_session)
    corpus = await repo.create_corpus(
        title="Trastuzumab Safety Surveillance",
        data_sources=["FDA_FAERS", "EudraVigilance"],
        total_reports=1200000
    )
    assert corpus.id is not None
    assert corpus.status == "ANALYZED"

    signal = await repo.add_signal(
        corpus_id=corpus.id,
        drug_name="Trastuzumab",
        adverse_reaction_term="Cardiotoxicity",
        system_organ_class="Cardiac disorders",
        case_count=120,
        signal_priority="URGENT",
        who_umc_causality="Probable",
        clinical_summary="Documented LVEF decline"
    )
    assert signal.id is not None

    metric = await repo.add_metrics(
        signal_id=signal.id,
        prr=3.5,
        ror=3.8,
        ror_lower=2.9,
        ror_upper=4.6,
        ic025=1.7,
        ebgm05=3.3,
        chi_sq=52.0
    )
    assert metric.id is not None

    fetched = await repo.get_corpus(corpus.id)
    assert len(fetched.signals) == 1
    assert len(fetched.signals[0].metrics) == 1
