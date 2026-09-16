"""
Tests for Phase 64: Peer Review Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.peer_review_repo import PeerReviewRepository


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
async def test_peer_review_repo_crud(async_session: AsyncSession):
    repo = PeerReviewRepository(async_session)

    # 1. Create Manuscript
    m = await repo.create_manuscript(
        manuscript_title="Autonomous Science Paper",
        research_domain="Bio-AI",
        abstract_text="We demonstrate AI scientist discovery.",
    )
    assert m.id is not None

    # 2. Add Reviews & Rebuttals
    updated = await repo.add_reviews_and_rebuttals(
        manuscript_id=m.id,
        reviews_data=[
            {
                "referee_persona": "Referee 1",
                "score_out_of_10": 8.5,
                "critique_summary": "Strong work",
                "rebuttals": [
                    {
                        "referee_claim": "Add power calculation",
                        "author_rebuttal": "Added in Note 4",
                    }
                ],
            }
        ],
        overall_score=8.5,
    )
    assert updated is not None
    assert updated.total_reviews == 1
    assert len(updated.reviews) == 1
    assert len(updated.reviews[0].rebuttal_points) == 1
