"""Tests for AcademicPaperParser in packages/ingestion."""

import io
import pytest
from ingestion.parsers.academic import AcademicPaperParser
from ingestion.parsers.base import PaperStructure, PaperSection, BibEntry


@pytest.fixture
def academic_parser() -> AcademicPaperParser:
    return AcademicPaperParser()


@pytest.mark.asyncio
async def test_academic_paper_parser_manuscript(academic_parser: AcademicPaperParser):
    sample_paper_text = (
        "Attention Is All You Need\n"
        "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit\n"
        "Google Brain, Google Research\n\n"
        "Abstract\n"
        "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. "
        "We propose the Transformer, a model architecture eschewing recurrence and relying entirely on attention mechanisms [1].\n\n"
        "1. Introduction\n"
        "Recurrent neural networks have been firmly established as state of the art in sequence modeling [2]. "
        "However, sequential computation precludes parallelization within training examples.\n\n"
        "2. Background\n"
        "The goal of reducing sequential computation also forms the foundation of Extended Neural GPU.\n\n"
        "3. Model Architecture\n"
        "Most competitive neural sequence transduction models have an encoder-decoder structure [3]. "
        "Here, the encoder maps an input sequence to continuous representations.\n\n"
        "4. Limitations\n"
        "The quadratic complexity with respect to sequence length limits the model for long contexts.\n\n"
        "5. References\n"
        "[1] Bahdanau et al. Neural machine translation by jointly learning to align and translate. ICLR 2015.\n"
        "[2] Hochreiter & Schmidhuber. Long short-term memory. Neural computation 1997.\n"
        "[3] Sutskever et al. Sequence to sequence learning with neural networks. NeurIPS 2014.\n"
    ).encode("utf-8")

    file_stream = io.BytesIO(sample_paper_text)
    doc = await academic_parser.parse(file_stream, filename="attention.txt")

    assert doc.metadata["format"] == "academic_paper"
    assert "Attention Is All You Need" in doc.metadata["title"]
    assert len(doc.metadata["authors"]) >= 3

    struct: PaperStructure = doc.paper_structure
    assert struct is not None
    assert struct.title == "Attention Is All You Need"
    assert "Ashish Vaswani" in struct.authors
    assert "Transformer" in struct.abstract

    # Check sections
    sec_types = [s.section_type for s in struct.sections]
    assert "introduction" in sec_types
    assert "methodology" in sec_types or "other" in sec_types
    assert "limitations" in sec_types
    assert "references" in sec_types

    # Check citations referenced
    intro_sec = next((s for s in struct.sections if s.section_type == "introduction"), None)
    assert intro_sec is not None
    assert "[2]" in intro_sec.citations_referenced

    # Check references
    assert len(struct.bibliography) == 3
    assert struct.bibliography[0].citation_key == "[1]"
    assert "Bahdanau" in struct.bibliography[0].raw_text
    assert struct.bibliography[0].year == 2015

    # Check markdown rendering
    md = struct.to_markdown()
    assert "# Attention Is All You Need" in md
    assert "## Abstract" in md
    assert "## References" in md
