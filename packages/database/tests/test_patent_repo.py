import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.patent import (
    DBFreedomToOperateReport,
    DBPatentClaim,
    DBPatentCorpus,
    DBPatentDocument,
    DBPriorArtEvaluation,
)
from database.repositories.patent_repo import PatentRepository


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
async def test_patent_repo_full_lifecycle(db_session: AsyncSession):
    """Test full Patent Corpus, Patent Document, Claim, 102/103 Evaluation, and FTO Report lifecycle."""
    repo = PatentRepository(db_session)
    user_id = uuid.uuid4()

    # 1. Create Patent Corpus
    corpus = DBPatentCorpus(
        user_id=user_id,
        title="Superconducting Qubit Architecture Landscape",
        technology_domain="quantum_computing",
        cpc_classification="G06N 10/00",
        jurisdiction="GLOBAL",
        status="active",
    )
    created_corpus = await repo.create_corpus(corpus)
    assert created_corpus.id is not None
    assert created_corpus.title == "Superconducting Qubit Architecture Landscape"

    # 2. Get Corpus
    fetched = await repo.get_corpus(created_corpus.id)
    assert fetched is not None
    assert len(fetched.patents) == 0

    # 3. Add Patent Document
    patent1 = DBPatentDocument(
        corpus_id=created_corpus.id,
        patent_number="US-11823901-B2",
        title="Quantum Fluxonium Qubit Readout",
        abstract="A method for readout using parametric amplification.",
        assignee="Quantum Flux Corp.",
        filing_date="2023-01-10",
        publication_date="2025-06-15",
        cpc_classes=["G06N 10/00"],
        status="granted",
        claims_count=1,
    )
    added_patent = await repo.add_patent(patent1)
    assert added_patent.id is not None

    # 4. Add Patent Claim
    claim = DBPatentClaim(
        patent_id=added_patent.id,
        claim_number=1,
        claim_type="independent",
        claim_text="A superconducting qubit circuit comprising: a Josephson junction; and a resonator.",
        parsed_elements_json=[{"element_id": "lim-1", "element_text": "a Josephson junction"}],
    )
    added_claim = await repo.add_claim(claim)
    assert added_claim.id is not None

    # 5. Record Prior Art Evaluation
    eval_record = DBPriorArtEvaluation(
        corpus_id=created_corpus.id,
        prior_art_patent_id=added_patent.id,
        target_invention_claim="A quantum processor comprising: a Josephson junction; a resonator; and a 3D waveguide cavity.",
        novelty_score=0.88,
        obviousness_score=0.20,
        overlap_ratio=0.33,
        verdict="distinguishable",
        detailed_rationale="The 3D waveguide cavity constitutes an unexpected novel limitation.",
    )
    saved_eval = await repo.record_prior_art_evaluation(eval_record)
    assert saved_eval.id is not None
    assert saved_eval.verdict == "distinguishable"

    # 6. Save FTO Report
    fto = DBFreedomToOperateReport(
        corpus_id=created_corpus.id,
        total_examined_patents=1,
        high_risk_claims_count=0,
        medium_risk_claims_count=0,
        fto_clearance_percentage=100.0,
        summary_assessment="High Freedom to Operate. Zero infringing claims.",
        white_space_opportunities=[{"domain_subfield": "3D Cavity Couplers", "patentability_index": 0.95}],
    )
    saved_fto = await repo.save_fto_report(fto)
    assert saved_fto.id is not None

    # 7. List Corpora
    corpora = await repo.list_corpora(user_id=user_id)
    assert len(corpora) == 1
    assert corpora[0].freedom_to_operate_verdict == "clear"

    # 8. Metrics
    metrics = await repo.get_patent_metrics()
    assert metrics["total_patent_corpora"] == 1
    assert metrics["total_patents_indexed"] == 1
    assert metrics["total_prior_art_evaluations"] == 1
    assert metrics["total_fto_reports"] == 1

    # 9. Delete Corpus
    assert await repo.delete_corpus(created_corpus.id) is True
    assert await repo.get_corpus(created_corpus.id) is None
