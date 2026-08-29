"""Chunking strategies for parsed documents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
from ingestion.parsers.base import ParsedDocument


@dataclass
class Chunk:
    """A semantic or fixed chunk of a document."""

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0
    chunk_index: int = 0


class ChunkingStrategy(ABC):
    """Abstract chunking strategy base class."""

    @abstractmethod
    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        """Split a parsed document into a list of chunks."""
        pass


class FixedSizeChunker(ChunkingStrategy):
    """Fixed-size overlapping character/word chunker."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        if overlap >= chunk_size:
            raise ValueError(f"Overlap ({overlap}) must be smaller than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        text = document.content
        if not text:
            return []

        chunks: List[Chunk] = []
        doc_name = document.metadata.get("filename", "doc")
        step = self.chunk_size - self.overlap
        start = 0
        index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]

            chunks.append(
                Chunk(
                    id=f"{doc_name}_chunk_{index}",
                    content=chunk_text,
                    metadata={**document.metadata, "chunk_index": index, "chunk_type": "fixed"},
                    start_char=start,
                    end_char=end,
                    chunk_index=index,
                )
            )

            if end >= len(text):
                break

            start += step
            index += 1

        return chunks


class SemanticChunker(ChunkingStrategy):
    """Semantic chunker splitting on headings, double newlines (paragraphs), and table boundaries."""

    def __init__(self, max_chunk_size: int = 2000, min_chunk_size: int = 100) -> None:
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        text = document.content
        if not text:
            return []

        doc_name = document.metadata.get("filename", "doc")
        paragraphs = text.split("\n\n")
        chunks: List[Chunk] = []

        current_parts: List[str] = []
        current_len = 0
        current_start = 0
        char_cursor = 0
        index = 0

        for p in paragraphs:
            p_len = len(p)
            # If adding this paragraph exceeds max size and we already have content
            if current_parts and (current_len + p_len + 2 > self.max_chunk_size):
                chunk_text = "\n\n".join(current_parts).strip()
                chunks.append(
                    Chunk(
                        id=f"{doc_name}_chunk_{index}",
                        content=chunk_text,
                        metadata={**document.metadata, "chunk_index": index, "chunk_type": "semantic"},
                        start_char=current_start,
                        end_char=current_start + len(chunk_text),
                        chunk_index=index,
                    )
                )
                index += 1
                current_parts = []
                current_len = 0
                current_start = char_cursor

            # If a single paragraph is longer than max_chunk_size, fall back to fixed chunking for it
            if p_len > self.max_chunk_size:
                if current_parts:
                    chunk_text = "\n\n".join(current_parts).strip()
                    chunks.append(
                        Chunk(
                            id=f"{doc_name}_chunk_{index}",
                            content=chunk_text,
                            metadata={**document.metadata, "chunk_index": index, "chunk_type": "semantic"},
                            start_char=current_start,
                            end_char=current_start + len(chunk_text),
                            chunk_index=index,
                        )
                    )
                    index += 1
                    current_parts = []
                    current_len = 0

                # Slice large paragraph into pieces
                for sub_start in range(0, p_len, self.max_chunk_size):
                    sub_text = p[sub_start : sub_start + self.max_chunk_size]
                    chunks.append(
                        Chunk(
                            id=f"{doc_name}_chunk_{index}",
                            content=sub_text.strip(),
                            metadata={**document.metadata, "chunk_index": index, "chunk_type": "semantic_split"},
                            start_char=char_cursor + sub_start,
                            end_char=char_cursor + sub_start + len(sub_text),
                            chunk_index=index,
                        )
                    )
                    index += 1
                char_cursor += p_len + 2
                current_start = char_cursor
                continue

            current_parts.append(p)
            current_len += p_len + 2
            char_cursor += p_len + 2

        if current_parts:
            chunk_text = "\n\n".join(current_parts).strip()
            chunks.append(
                Chunk(
                    id=f"{doc_name}_chunk_{index}",
                    content=chunk_text,
                    metadata={**document.metadata, "chunk_index": index, "chunk_type": "semantic"},
                    start_char=current_start,
                    end_char=current_start + len(chunk_text),
                    chunk_index=index,
                )
            )

        return chunks
