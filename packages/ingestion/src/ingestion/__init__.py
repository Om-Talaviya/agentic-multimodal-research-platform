"""Multimodal Ingestion Package for Agentic Multimodal Research Platform."""

from ingestion.chunking import Chunk, ChunkingStrategy, FixedSizeChunker, SemanticChunker
from ingestion.detection import detect_format
from ingestion.parsers import (
    DocxParser,
    DocumentParser,
    ImageParser,
    ImageRef,
    ParsedDocument,
    ParserRegistry,
    PDFParser,
    Table,
    TextParser,
)
from ingestion.pipeline import IngestionPipeline, IngestionResult
from shared.types import DocumentFormat

__all__ = [
    "detect_format",
    "DocumentFormat",
    "DocumentParser",
    "ParsedDocument",
    "ImageRef",
    "Table",
    "TextParser",
    "PDFParser",
    "DocxParser",
    "ImageParser",
    "ParserRegistry",
    "Chunk",
    "ChunkingStrategy",
    "FixedSizeChunker",
    "SemanticChunker",
    "IngestionPipeline",
    "IngestionResult",
]
