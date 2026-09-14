import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.peer_review import (
    DBManuscriptRevision,
    DBPeerReviewManuscript,
    DBPeerReviewReport,
)
from database.repositories.peer_review_repo import PeerReviewRepository


@pytest.fixture
async def db_session():
    """Create in-memory SQLite database session for testing."""
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
async def test_peer_review_repo_full_lifecycle(db_session: AsyncSession):

    """Test full manuscript lifecycle: create, list, review reports, revisions, publishing, and metrics."""
    repo = PeerReviewRepository(db_session)
    user_id = uuid.uuid4()

    # 1. Create manuscript
    manuscript = DBPeerReviewManuscript(
        user_id=user_id,
        title="Zero-Entropy Information Compression in Deep Multimodal Transformers",
        abstract="A mathematical and empirical proof for lossless compression across heterogeneous modalities.",
        field_of_study="computer_science",
        venue_format="nature",
        claimed_contributions=["Lossless multimodal bounds", "Empirical 4.2% accuracy improvement"],
        keywords=["Compression", "Multimodal", "Transformers"],
    )
    created = await repo.create_manuscript(manuscript)
    assert created.id is not None
    assert created.title.startswith("Zero-Entropy")
    assert created.status == "submitted"

    # 2. Get manuscript
    fetched = await repo.get_manuscript(created.id)
    assert fetched is not None
    assert fetched.venue_format == "nature"
    assert len(fetched.reports) == 0

    # 3. List manuscripts
    listed = await repo.list_manuscripts(user_id=user_id)
    assert len(listed) >= 1
    assert listed[0].id == created.id

    # 4. Save referee reports
    reports = [
        DBPeerReviewReport(
            reviewer_persona="methodology_critic",
            reviewer_title="Senior Methodologist",
            originality_score=8.5,
            methodology_score=9.0,
            empirical_soundness=8.5,
            clarity_score=8.0,
            composite_score=8.65,
            recommendation="accept",
            summary_verdict="Sound methodology and proofs.",
            strengths=["Strong proofs"],
            weaknesses=["Minor baseline clarity"],
            detailed_critique="Detailed review comments here.",
            required_revisions=["Clarify baseline dataset setup"],
        ),
        DBPeerReviewReport(
            reviewer_persona="statistical_auditor",
            reviewer_title="Statistical Significance Auditor",
            originality_score=8.0,
            methodology_score=8.5,
            empirical_soundness=9.2,
            clarity_score=8.5,
            composite_score=8.75,
            recommendation="accept",
            summary_verdict="Statistically significant across all tests.",
            strengths=["P-values reported"],
            weaknesses=[],
            detailed_critique="No major concerns.",
            required_revisions=[],
        ),
    ]
    saved_reports = await repo.save_peer_review_reports(created.id, reports)
    assert len(saved_reports) == 2

    # Verify manuscript score and status updated
    updated_m = await repo.get_manuscript(created.id)
    assert updated_m.overall_score == 8.70
    assert updated_m.status == "accepted"

    # 5. Add manuscript revision
    revision = DBManuscriptRevision(
        manuscript_id=created.id,
        revision_round=1,
        rebuttal_letter="We thank the reviewers for their positive evaluation.",
        diff_summary="Clarified baseline dataset setup in Section 3.",
        point_by_point_responses=[{"reviewer_id": "Reviewer 1", "comment": "Baseline setup clarified"}],
        status="submitted",
    )
    added_rev = await repo.add_manuscript_revision(revision)
    assert added_rev.revision_round == 1

    # 6. Publish manuscript
    published = await repo.publish_manuscript(
        manuscript_id=created.id,
        doi="10.1038/s41586-026.zeroentropy-8921a4",
        latex="\\documentclass{article}...",
        bibtex="@article{talaviya2026zeroentropy}...",
    )
    assert published.status == "published"
    assert published.camera_ready_doi == "10.1038/s41586-026.zeroentropy-8921a4"

    # 7. Query metrics
    metrics = await repo.get_peer_review_metrics()
    assert metrics["total_manuscripts"] >= 1
    assert metrics["total_referee_reports"] >= 2
    assert metrics["acceptance_rate"] > 0.0

    # 8. Delete manuscript
    deleted = await repo.delete_manuscript(created.id)
    assert deleted is True
    assert await repo.get_manuscript(created.id) is None
