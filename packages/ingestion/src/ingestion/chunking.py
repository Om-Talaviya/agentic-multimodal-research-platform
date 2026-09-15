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
    """Semantic chunker splitting on headings, double newlines, audio timestamps, and chart boundaries."""

    def __init__(self, max_chunk_size: int = 2000, min_chunk_size: int = 100) -> None:
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        chunks: List[Chunk] = []
        doc_name = document.metadata.get("filename", "doc")
        index = 0

        # 1. Handle Audio/Video segments with timestamps
        if document.audio_segments:
            for s in document.audio_segments:
                start_min = int(s.start_seconds // 60)
                start_sec = int(s.start_seconds % 60)
                end_min = int(s.end_seconds // 60)
                end_sec = int(s.end_seconds % 60)
                ts_header = f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}]"
                speaker_str = f" ({s.speaker})" if s.speaker else ""
                chunk_text = f"{ts_header}{speaker_str}: {s.text}"

                media_type = document.metadata.get("format", "audio")
                chunks.append(
                    Chunk(
                        id=f"{doc_name}_audio_chunk_{index}",
                        content=chunk_text,
                        metadata={
                            **document.metadata,
                            "chunk_index": index,
                            "chunk_type": "audio_segment",
                            "media_type": media_type,
                            "timestamp_start": s.start_seconds,
                            "timestamp_end": s.end_seconds,
                            "timestamp_str": f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}",
                            "speaker": s.speaker,
                            "confidence": s.confidence,
                        },
                        start_char=0,
                        end_char=len(chunk_text),
                        chunk_index=index,
                    )
                )
                index += 1

            # If audio segments cover the full document, return chunk list
            if chunks:
                return chunks

        # 2. Handle Structured Scientific Charts
        if document.charts:
            for c in document.charts:
                chart_md = c.to_markdown()
                chunks.append(
                    Chunk(
                        id=f"{doc_name}_chart_chunk_{index}",
                        content=chart_md,
                        metadata={
                            **document.metadata,
                            "chunk_index": index,
                            "chunk_type": "chart_series",
                            "media_type": "chart",
                            "chart_type": c.chart_type,
                            "chart_title": c.title,
                            "chart_data": c.data_series,
                            "page_number": c.page_number,
                        },
                        start_char=0,
                        end_char=len(chart_md),
                        chunk_index=index,
                    )
                )
                index += 1

        # 3. Handle Tabular Datasets & Statistical Profiles
        if document.dataset_profile:
            profile = document.dataset_profile
            profile_md = profile.to_markdown()
            chunks.append(
                Chunk(
                    id=f"{doc_name}_dataset_profile_chunk_{index}",
                    content=profile_md,
                    metadata={
                        **document.metadata,
                        "chunk_index": index,
                        "chunk_type": "dataset_profile",
                        "media_type": "dataset",
                        "total_rows": profile.total_rows,
                        "total_cols": profile.total_cols,
                        "columns": [c.name for c in profile.columns],
                        "numeric_columns": [c.name for c in profile.columns if c.data_type in ("integer", "float")],
                    },
                    start_char=0,
                    end_char=len(profile_md),
                    chunk_index=index,
                )
            )
            index += 1

            # If dataset profile covers the file, return chunks
            if chunks:
                return chunks

        # 4. Handle Academic Research Papers with Section Trees
        if document.paper_structure:
            paper = document.paper_structure
            # 4a. Abstract Chunk
            if paper.abstract:
                abstract_text = f"**Paper: {paper.title}**\n**Authors**: {', '.join(paper.authors)}\n\n### Abstract\n{paper.abstract}"
                chunks.append(
                    Chunk(
                        id=f"{doc_name}_paper_abstract_{index}",
                        content=abstract_text,
                        metadata={
                            **document.metadata,
                            "chunk_index": index,
                            "chunk_type": "academic_abstract",
                            "section_type": "abstract",
                            "section_title": "Abstract",
                            "paper_title": paper.title,
                            "authors": paper.authors,
                        },
                        start_char=0,
                        end_char=len(abstract_text),
                        chunk_index=index,
                    )
                )
                index += 1

            # 4b. Section Chunks
            for sec in paper.sections:
                if not sec.content:
                    continue

                sec_header = f"**Paper: {paper.title}**\n### Section: {sec.title} ({sec.section_type})"
                sec_full = f"{sec_header}\n\n{sec.content}"

                if len(sec_full) <= self.max_chunk_size:
                    chunks.append(
                        Chunk(
                            id=f"{doc_name}_sec_{sec.section_id}_{index}",
                            content=sec_full,
                            metadata={
                                **document.metadata,
                                "chunk_index": index,
                                "chunk_type": "academic_section",
                                "section_id": sec.section_id,
                                "section_type": sec.section_type,
                                "section_title": sec.title,
                                "paper_title": paper.title,
                                "authors": paper.authors,
                                "citations_referenced": sec.citations_referenced,
                            },
                            start_char=0,
                            end_char=len(sec_full),
                            chunk_index=index,
                        )
                    )
                    index += 1
                else:
                    # Subdivide long section paragraphs
                    paras = sec.content.split("\n\n")
                    sub_parts: List[str] = []
                    sub_len = 0
                    for p in paras:
                        if sub_parts and (sub_len + len(p) + 2 > self.max_chunk_size - len(sec_header) - 10):
                            sub_text = f"{sec_header}\n\n" + "\n\n".join(sub_parts)
                            chunks.append(
                                Chunk(
                                    id=f"{doc_name}_sec_{sec.section_id}_{index}",
                                    content=sub_text,
                                    metadata={
                                        **document.metadata,
                                        "chunk_index": index,
                                        "chunk_type": "academic_section",
                                        "section_id": sec.section_id,
                                        "section_type": sec.section_type,
                                        "section_title": sec.title,
                                        "paper_title": paper.title,
                                        "authors": paper.authors,
                                        "citations_referenced": sec.citations_referenced,
                                    },
                                    start_char=0,
                                    end_char=len(sub_text),
                                    chunk_index=index,
                                )
                            )
                            index += 1
                            sub_parts = [p]
                            sub_len = len(p)
                        else:
                            sub_parts.append(p)
                            sub_len += len(p) + 2
                    if sub_parts:
                        sub_text = f"{sec_header}\n\n" + "\n\n".join(sub_parts)
                        chunks.append(
                            Chunk(
                                id=f"{doc_name}_sec_{sec.section_id}_{index}",
                                content=sub_text,
                                metadata={
                                    **document.metadata,
                                    "chunk_index": index,
                                    "chunk_type": "academic_section",
                                    "section_id": sec.section_id,
                                    "section_type": sec.section_type,
                                    "section_title": sec.title,
                                    "paper_title": paper.title,
                                    "authors": paper.authors,
                                    "citations_referenced": sec.citations_referenced,
                                },
                                start_char=0,
                                end_char=len(sub_text),
                                chunk_index=index,
                            )
                        )
                        index += 1

            if chunks:
                return chunks

        # 5. Standard Text / Paragraph Semantic Chunking
        text = document.content
        if not text:
            return chunks

        paragraphs = text.split("\n\n")
        current_parts: List[str] = []
        current_len = 0
        current_start = 0
        char_cursor = 0

        for p in paragraphs:
            p_len = len(p)
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

