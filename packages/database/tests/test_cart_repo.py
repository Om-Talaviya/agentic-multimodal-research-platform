import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.cart_engineering_repo import CARTRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()

@pytest.mark.asyncio
async def test_cart_repo_create_and_query(async_session: AsyncSession):
    repo = CARTRepository(async_session)
    construct = await repo.create_construct(
        construct_name="Test-CART-CD19",
        target_antigen="CD19",
        scfv_binder_clone="FMC63",
        costimulatory_domain="4-1BB",
    )
    assert construct.id is not None
    assert construct.target_antigen == "CD19"

    scorecard = await repo.add_cytotoxicity_scorecard(
        construct_id=construct.id,
        target_cell_line="Raji",
        effector_to_target_ratio=5.0,
        specific_lysis_pct=92.5,
        t_cell_persistence_score=0.88,
        exhaustion_pd1_expression_pct=14.5,
        exhaustion_tim3_expression_pct=12.0,
        exhaustion_lag3_expression_pct=9.5,
    )
    assert scorecard.id is not None
    assert scorecard.specific_lysis_pct == 92.5

    profile = await repo.add_crs_toxicity_profile(
        construct_id=construct.id,
        peak_il6_pg_ml=165.0,
        peak_ifng_pg_ml=210.0,
        peak_tnfa_pg_ml=85.0,
        peak_il1b_pg_ml=38.0,
        astct_crs_grade_predicted="Grade 2",
        icans_neurotoxicity_risk_pct=22.0,
    )
    assert profile.id is not None
    assert profile.astct_crs_grade_predicted == "Grade 2"

    fetched = await repo.get_construct(construct.id)
    assert fetched is not None
    assert len(fetched.cytotoxicity_scorecards) == 1
    assert len(fetched.crs_profiles) == 1
