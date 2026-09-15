"""Unit tests for LiteratureRepository, PRISMA models, and Meta-Analysis records."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.user import User
from database.repositories.literature_repo import LiteratureRepository


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
async def test_literature_repo_full_lifecycle(db_session: AsyncSession):
    """Test SLR review creation, criteria, study candidates, screening, RoB, and meta-analysis persistence."""
    user = User(
        id=uuid.uuid4(),
        username="slr_researcher",
        email="slr@test.com",
        password_hash="hashed_pw",
        role="researcher",
    )
    db_session.add(user)
    await db_session.commit()

    repo = LiteratureRepository(db_session)

    # 1. Create SLR Review
    review = await repo.create_literature_review(
        user_id=user.id,
        title="Agentic Multimodal Reasoning in Clinical Pathology",
        research_question="Does multimodal agentic chain-of-thought reduce diagnostic error compared to single-agent baselines?",
        protocol_type="PRISMA-2020",
        pico_framework={
            "population": "Digital Whole Slide Pathology Images",
            "intervention": "Multimodal Agentic CoT",
            "comparator": "Single-Agent Vision LLM Baseline",
            "outcome": "Diagnostic Error Rate / F1 Score",
        },
    )
    assert review.id is not None
    assert review.current_phase == "identification"
    assert review.total_identified == 0

    # 2. Add Inclusion/Exclusion Criteria
    crit_inc = await repo.add_criterion(
        review_id=review.id,
        criterion_type="inclusion",
        description="Peer-reviewed studies evaluating multimodal models on medical images",
        category="study_design",
        order_index=1,
    )
    crit_exc = await repo.add_criterion(
        review_id=review.id,
        criterion_type="exclusion",
        description="Studies lacking quantitative accuracy or variance metrics",
        category="methodology",
        order_index=2,
    )
    assert crit_inc.id is not None
    assert crit_exc.id is not None

    criteria_list = await repo.list_criteria(review.id)
    assert len(criteria_list) == 2

    # 3. Add Candidate Studies
    candidates = await repo.add_candidate_studies(
        review_id=review.id,
        studies=[
            {
                "title": "AgentPath: Multi-Agent CoT on Histopathology (2025)",
                "authors": ["Smith et al."],
                "publication_year": 2025,
                "screening_status": "identified",
                "sample_size": 250,
                "effect_size": 0.62,
                "variance": 0.04,
            },
            {
                "title": "Single-turn Vision Pathology Baseline (2024)",
                "authors": ["Johnson et al."],
                "publication_year": 2024,
                "screening_status": "identified",
                "sample_size": 180,
                "effect_size": 0.48,
                "variance": 0.05,
            },
            {
                "title": "Qualitative Case Studies on Pathology AI (2023)",
                "authors": ["Brown et al."],
                "publication_year": 2023,
                "screening_status": "identified",
                "sample_size": 12,
            },
        ],
    )
    assert len(candidates) == 3

    # Check updated review counts
    updated_review = await repo.get_literature_review(review.id)
    assert updated_review.total_identified == 3

    # 4. Screen Candidates (Include 2, Exclude 1)
    cand_1 = candidates[0]
    cand_2 = candidates[1]
    cand_3 = candidates[2]

    await repo.update_candidate_screening(
        candidate_id=cand_1.id,
        screening_status="included",
        methodology_type="Benchmark Experiment",
    )
    await repo.update_candidate_screening(
        candidate_id=cand_2.id,
        screening_status="included",
        methodology_type="Comparative Evaluation",
    )
    await repo.update_candidate_screening(
        candidate_id=cand_3.id,
        screening_status="excluded",
        exclusion_reason="Sample size too small (< 20) and no quantitative variance reported",
    )

    refreshed_review = await repo.get_literature_review(review.id)
    assert refreshed_review.total_included == 2
    assert refreshed_review.total_excluded == 1

    # 5. Add Risk of Bias Assessment for Included Candidate
    rob = await repo.save_risk_of_bias(
        candidate_id=cand_1.id,
        selection_bias="low_risk",
        confounding_bias="low_risk",
        measurement_bias="low_risk",
        reporting_bias="low_risk",
        overall_risk="low_risk",
        justification_notes="Double-blind benchmark validation on standard Camelyon16 dataset.",
    )
    assert rob.id is not None
    assert rob.overall_risk == "low_risk"

    # 6. Save Meta-Analysis Report
    meta_rep = await repo.save_meta_analysis_report(
        review_id=review.id,
        synthesis_name="Pathology Diagnostic Accuracy Synthesis",
        effect_metric="hedges_g",
        model_type="random_effects",
        total_studies_analyzed=2,
        pooled_effect_size=0.556,
        pooled_ci_lower=0.321,
        pooled_ci_upper=0.791,
        pooled_p_value=0.0001,
        z_score=4.63,
        q_statistic=0.48,
        degrees_of_freedom=1,
        i_squared=0.0,
        tau_squared=0.0,
        forest_plot_data=[
            {"study_id": str(cand_1.id), "title": cand_1.title, "effect_size": 0.62, "weight_percentage": 55.5},
            {"study_id": str(cand_2.id), "title": cand_2.title, "effect_size": 0.48, "weight_percentage": 44.5},
        ],
    )
    assert meta_rep.id is not None
    assert meta_rep.pooled_effect_size == 0.556

    # 7. Check Metrics
    metrics = await repo.get_slr_metrics()
    assert metrics["total_reviews"] == 1
    assert metrics["total_candidates"] == 3
    assert metrics["total_included_studies"] == 2
    assert metrics["total_meta_analyses"] == 1
