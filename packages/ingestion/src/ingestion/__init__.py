"""Multimodal Ingestion Package for Agentic Multimodal Research Platform."""

from ingestion.chunking import Chunk, ChunkingStrategy, FixedSizeChunker, SemanticChunker
from ingestion.detection import detect_format
from ingestion.parsers import (
    AcademicPaperParser,
    AudioParser,
    AudioSegment,
    BibEntry,
    ChartRef,
    ColumnProfile,
    DatasetProfile,
    DocumentParser,
    DocxParser,
    ImageParser,
    ImageRef,
    PaperSection,
    PaperStructure,
    ParsedDocument,
    ParserRegistry,
    PDFParser,
    Table,
    TabularParser,
    TextParser,
    VideoParser,
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
    "AudioSegment",
    "ChartRef",
    "ColumnProfile",
    "DatasetProfile",
    "PaperSection",
    "BibEntry",
    "PaperStructure",
    "AcademicPaperParser",
    "TextParser",
    "PDFParser",
    "DocxParser",
    "TabularParser",
    "ImageParser",
    "AudioParser",
    "VideoParser",
    "ParserRegistry",
    "Chunk",
    "ChunkingStrategy",
    "FixedSizeChunker",
    "SemanticChunker",
    "IngestionPipeline",
    "IngestionResult",
]
