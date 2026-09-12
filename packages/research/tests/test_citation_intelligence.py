"""Tests for Citation and Evidence Intelligence (Phase 10)."""

from uuid import uuid4
import pytest
from research.models import (
    CitationCoordinates,
    Citation,
    Contradiction,
    Evidence,
    Finding,
    ResearchReport,
    Source,
)
from database.models import Evidence as DBEvidence, Report as DBReport
from research.pipeline import ResearchPipeline


def test_citation_coordinates_and_model_instantiation():
    """Verify CitationCoordinates and Citation creation and serialization."""
    coords = CitationCoordinates(
        page_number=3,
        paragraph_index=2,
        table_row=4,
        table_col=1,
        char_start=150,
        char_end=220,
    )
    assert coords.page_number == 3
    assert coords.paragraph_index == 2
    assert coords.table_row == 4
    assert coords.table_col == 1

    citation = Citation(
        claim="Transformer self-attention scales quadratically with sequence length.",
        source_id="src-101",
        document_id="doc-404",
        citation_text="Section 3.2, Page 3",
        quote="Self-attention layers have O(n^2) computational complexity.",
        coordinates=coords,
        confidence=0.96,
        source_reliability=1.0,
    )

    dumped = citation.model_dump()
    assert dumped["claim"] == "Transformer self-attention scales quadratically with sequence length."
    assert dumped["coordinates"]["page_number"] == 3
    assert dumped["coordinates"]["char_start"] == 150
    assert dumped["confidence"] == 0.96


def test_contradiction_model_creation():
    """Verify Contradiction data model validation and taxonomy."""
    contradiction = Contradiction(
        topic="Model Training FLOPs",
        claim_a="The model was trained on 2.5e24 FLOPs.",
        source_a="Technical Report v1",
        claim_b="The model required 3.8e24 total compute FLOPs.",
        source_b="Conference Proceedings",
        conflict_type="numerical_discrepancy",
        explanation="Version 1 only included pretraining FLOPs, whereas the conference paper includes RLHF compute.",
        severity="high",
    )

    assert contradiction.conflict_type == "numerical_discrepancy"
    assert contradiction.severity == "high"
    assert "2.5e24" in contradiction.claim_a
    assert "3.8e24" in contradiction.claim_b


def test_db_evidence_conversion_with_coordinates_and_reliability():
    """Verify ResearchPipeline._convert_to_db_evidence maps coordinates and source reliability."""
    job_uuid = uuid4()
    coords = CitationCoordinates(page_number=5, paragraph_index=1)
    ev = Evidence(
        id=str(uuid4()),
        source_id=str(uuid4()),
        claim="Fine-tuning improves retrieval precision by 22%.",
        supporting_text="Experiments in Table 3 show a 22% increase in precision.",
        confidence=0.92,
        verification_status="verified",
        coordinates=coords,
    )

    db_ev = ResearchPipeline._convert_to_db_evidence(ev, job_uuid)
    assert isinstance(db_ev, DBEvidence)
    assert db_ev.claim == "Fine-tuning improves retrieval precision by 22%."
    assert db_ev.confidence == 0.92
    assert db_ev.citation_coordinates["page_number"] == 5
    assert db_ev.citation_coordinates["paragraph_index"] == 1


def test_research_report_with_citations_and_contradictions():
    """Verify ResearchReport supports structured citations, contradictions, and confidence score."""
    job_id = str(uuid4())
    citation = Citation(
        claim="Vision encoder extracts 256 tokens per image.",
        citation_text="Page 4, Architecture Diagram",
        quote="Each 336x336 image is mapped to 256 embedding tokens.",
    )
    finding = Finding(
        topic="Vision Architecture",
        summary="Image patches are converted to dense visual tokens [cit_1].",
        citations=[citation],
        confidence=0.9,
    )
    contradiction = Contradiction(
        topic="Context Length",
        claim_a="Maximum context length is 8k tokens.",
        source_a="Source A",
        claim_b="Maximum context length is 16k tokens.",
        source_b="Source B",
        conflict_type="direct_conflict",
        explanation="Discrepancy between release candidate and final release.",
        severity="medium",
    )

    report = ResearchReport(
        job_id=job_id,
        title="Multimodal Architecture Analysis",
        executive_summary="Summary of architecture.",
        methodology="Review of paper specifications.",
        findings=[finding],
        contradictions=[contradiction],
        confidence_score=0.91,
        conclusions=["Model uses hybrid tokenization."],
        limitations=["Longer sequences not tested."],
    )

    data = report.model_dump()
    assert len(data["findings"]) == 1
    assert len(data["findings"][0]["citations"]) == 1
    assert data["findings"][0]["citations"][0]["quote"] == "Each 336x336 image is mapped to 256 embedding tokens."
    assert len(data["contradictions"]) == 1
    assert data["contradictions"][0]["conflict_type"] == "direct_conflict"
    assert data["confidence_score"] == 0.91
