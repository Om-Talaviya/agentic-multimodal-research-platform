"""Unit tests for PresentationRepository and database models."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.user import User
from database.repositories.presentation_repo import PresentationRepository


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
async def test_presentation_repo_lifecycle(db_session: AsyncSession):
    """Test creating presentation decks, adding slides, and persisting podcast audio briefings."""
    user = User(
        id=uuid.uuid4(),
        username="presenter_test",
        email="presenter@test.com",
        password_hash="hashed_pw",
        role="researcher",
    )
    db_session.add(user)
    await db_session.commit()

    repo = PresentationRepository(db_session)

    # 1. Create Presentation
    pres = await repo.create_presentation(
        user_id=user.id,
        title="Emergent Multimodal Reasoning in Clinical Pathology",
        subtitle="Executive & Clinical Leadership Briefing",
        target_audience="executive",
        theme="midnight_slate",
        estimated_duration_min=15,
    )
    assert pres.id is not None
    assert pres.title == "Emergent Multimodal Reasoning in Clinical Pathology"
    assert pres.total_slides == 0

    # 2. Add Slides Batch
    slides = await repo.add_presentation_slides_batch(
        presentation_id=pres.id,
        slides_data=[
            {
                "slide_number": 1,
                "layout_type": "title",
                "headline": "Emergent Multimodal Reasoning in Clinical Pathology",
                "bullet_points": ["Executive Briefing 2026", "Authored by Autonomous Agentic Pipeline"],
                "speaker_notes": "Welcome everyone to the executive synthesis.",
            },
            {
                "slide_number": 2,
                "layout_type": "bullet_points",
                "headline": "Core Breakthroughs & Effect Sizes",
                "bullet_points": ["Achieved +24% diagnostic precision.", "Validated on 1,000 whole-slide images."],
                "speaker_notes": "The primary outcome shows strong statistical significance.",
            },
        ],
    )
    assert len(slides) == 2

    # Fetch eager presentation
    fetched_pres = await repo.get_presentation(pres.id)
    assert fetched_pres.total_slides == 2
    assert len(fetched_pres.slides) == 2

    # 3. Create Podcast Audio Briefing
    podcast = await repo.create_podcast_briefing(
        user_id=user.id,
        title="Pathology AI: The Deep Dive",
        episode_topic="Multimodal AI vs Human Pathology Baselines",
        host_name="Dr. Elena Vance (Host)",
        expert_name="Prof. Marcus Sterling (Specialist)",
        total_duration_sec=120.0,
        dialogue_transcript_json=[
            {
                "turn_index": 1,
                "speaker": "Dr. Elena Vance (Host)",
                "text": "Welcome to the podcast. Marcus, tell us about the latest findings.",
                "audio_cue": "[warm intro]",
                "timestamp_start_sec": 0.0,
                "timestamp_end_sec": 10.0,
                "duration_sec": 10.0,
            },
            {
                "turn_index": 2,
                "speaker": "Prof. Marcus Sterling (Specialist)",
                "text": "The in-silico simulation reproduced the claimed accuracy gain.",
                "audio_cue": "[enthusiastic]",
                "timestamp_start_sec": 10.0,
                "timestamp_end_sec": 25.0,
                "duration_sec": 15.0,
            },
        ],
    )
    assert podcast.id is not None
    assert podcast.total_dialogue_turns == 2

    # 4. Check Platform Metrics
    metrics = await repo.get_presentation_metrics()
    assert metrics["total_presentations"] == 1
    assert metrics["total_slides"] == 2
    assert metrics["total_podcasts"] == 1
    assert metrics["total_audio_minutes"] == 2.0
