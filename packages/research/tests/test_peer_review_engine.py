"""Unit tests for PeerReviewEngine, PublicationFormatter, and AuthorRebuttalGenerator."""

import pytest
from research.publishing.peer_review import (
    AuthorRebuttalGenerator,
    PeerReviewEngine,
    PublicationFormatter,
)


def test_peer_review_engine_multi_agent_evaluation():
    """Test multi-agent blind peer review with methodology, statistical, and domain personas."""
    title = "Theoretical Foundations of Asymmetric Multi-Modal Contrastive Losses"
    abstract = "We rigorously derive gradient convergence conditions for asymmetric multimodal contrastive learning under unbounded support."
    contributions = [
        "Proof of asymptotic consistency for asymmetric projectors",
        "Empirical validation across ImageNet, AudioSet, and MIMIC-IV benchmarks",
    ]

    result = PeerReviewEngine.evaluate_manuscript(
        title=title,
        abstract=abstract,
        field_of_study="computer_science",
        claimed_contributions=contributions,
        venue_format="nature",
    )

    assert "editorial_decision" in result
    assert result["editorial_decision"] in ("accepted", "revisions_requested", "under_review", "rejected")
    assert 5.0 <= result["average_composite_score"] <= 10.0

    reports = result["referee_reports"]
    assert len(reports) == 3

    personas = {r["reviewer_persona"] for r in reports}
    assert personas == {"methodology_critic", "statistical_auditor", "domain_specialist"}

    for r in reports:
        assert 0.0 <= r["originality_score"] <= 10.0
        assert 0.0 <= r["methodology_score"] <= 10.0
        assert 0.0 <= r["empirical_soundness"] <= 10.0
        assert 0.0 <= r["clarity_score"] <= 10.0
        assert len(r["strengths"]) >= 1
        assert len(r["weaknesses"]) >= 1
        assert len(r["required_revisions"]) >= 1
        assert r["recommendation"] in ("accept", "minor_revision", "major_revision", "reject")


def test_publication_formatter():
    """Test DOI minting, BibTeX generation, and LaTeX camera-ready template synthesis."""
    title = "Quantum Tensor Network Simulation on High-Performance Clusters"
    abstract = "Scalable simulation of 128-qubit circuits using distributed matrix product states."
    authors = ["Dr. Sarah Lin", "Prof. Alan Turing"]

    # 1. DOI Generation
    doi = PublicationFormatter.generate_doi(title, venue_format="nature")
    assert doi.startswith("10.1038/s41586-026.")
    assert "quantumtenso" in doi

    # 2. BibTeX Generation
    bibtex = PublicationFormatter.generate_bibtex(
        title=title,
        authors=authors,
        year=2026,
        doi=doi,
        venue_format="nature",
    )
    assert "@article{" in bibtex
    assert "Dr. Sarah Lin and Prof. Alan Turing" in bibtex
    assert doi in bibtex

    # 3. LaTeX Generation
    latex = PublicationFormatter.generate_latex_source(
        title=title,
        abstract=abstract,
        authors=authors,
        doi=doi,
        venue_format="nature",
    )
    assert "\\documentclass" in latex
    assert "\\title{Quantum Tensor Network Simulation on High-Performance Clusters}" in latex
    assert "\\begin{abstract}" in latex
    assert "\\begin{document}" in latex


def test_author_rebuttal_generator():
    """Test automated point-by-point author rebuttal letter generation."""
    reports = [
        {
            "reviewer_persona": "methodology_critic",
            "reviewer_title": "Senior Methodologist",
            "required_revisions": ["Provide ablation on sparse matrices"],
            "weaknesses": ["Baseline comparison lacks 2026 benchmark"],
        },
        {
            "reviewer_persona": "statistical_auditor",
            "reviewer_title": "Statistical Auditor",
            "required_revisions": ["Report confidence intervals in Table 2"],
            "weaknesses": [],
        },
    ]

    rebuttal = AuthorRebuttalGenerator.generate_rebuttal(
        manuscript_title="Quantum Tensor Network Simulation",
        reports=reports,
        revision_round=1,
    )

    assert "Dear Editor and Referees" in rebuttal["rebuttal_letter"]
    assert len(rebuttal["point_by_point_responses"]) >= 3
    for resp in rebuttal["point_by_point_responses"]:
        assert "reviewer_id" in resp
        assert "author_response" in resp
        assert "action_taken" in resp
