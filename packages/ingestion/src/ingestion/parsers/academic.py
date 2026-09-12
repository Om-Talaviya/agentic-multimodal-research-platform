"""Academic paper parser extracting hierarchical section trees, bibliographies, and benchmarks."""

import asyncio
import io
import re
from typing import BinaryIO, Dict, List, Optional, Tuple, Any
from uuid import uuid4

from ingestion.parsers.base import (
    DocumentParser,
    ParsedDocument,
    PaperSection,
    BibEntry,
    PaperStructure,
    Table,
    ChartRef,
)
from shared.logging import get_logger
from shared.types import DocumentFormat

logger = get_logger(__name__)

# Section classification pattern mapping
SECTION_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("abstract", re.compile(r"^(?:abstract)\b", re.IGNORECASE)),
    ("introduction", re.compile(r"^(?:\d+\.?\s*)?(?:introduction|background)\b", re.IGNORECASE)),
    ("related_work", re.compile(r"^(?:\d+\.?\s*)?(?:related\s+work|prior\s+work|literature\s+review)\b", re.IGNORECASE)),
    ("methodology", re.compile(r"^(?:\d+\.?\s*)?(?:methodology|methods?|approach|model\s+architecture|system\s+design|formulation)\b", re.IGNORECASE)),
    ("experiments", re.compile(r"^(?:\d+\.?\s*)?(?:experiments?|experimental\s+setup|evaluation|empirical\s+evaluation)\b", re.IGNORECASE)),
    ("results", re.compile(r"^(?:\d+\.?\s*)?(?:results|findings|experimental\s+results|main\s+results)\b", re.IGNORECASE)),
    ("discussion", re.compile(r"^(?:\d+\.?\s*)?(?:discussion|ablation\s+studies?|analysis)\b", re.IGNORECASE)),
    ("limitations", re.compile(r"^(?:\d+\.?\s*)?(?:limitations?|threats\s+to\s+validity|broader\s+impacts?)\b", re.IGNORECASE)),
    ("conclusion", re.compile(r"^(?:\d+\.?\s*)?(?:conclusion|conclusions|concluding\s+remarks|future\s+work)\b", re.IGNORECASE)),
    ("references", re.compile(r"^(?:\d+\.?\s*)?(?:references|bibliography)\b", re.IGNORECASE)),
    ("appendix", re.compile(r"^(?:appendix|supplementary\s+material)\b", re.IGNORECASE)),
]

CITATION_REGEX = re.compile(r"\[(\d+(?:,\s*\d+)*)\]|\(([A-Z][a-zA-Z]+(?:\s+et\s+al\.)?,\s*\d{4})\)")


class AcademicPaperParser(DocumentParser):
    """Parses academic research papers (PDF, LaTeX, Markdown/Text) into structured section trees."""

    @property
    def supported_formats(self) -> List[DocumentFormat]:
        return [DocumentFormat.PDF, DocumentFormat.TEXT, DocumentFormat.MARKDOWN]

    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        return await asyncio.to_thread(self._parse_sync, file, filename)

    def _parse_sync(self, file: BinaryIO, filename: str) -> ParsedDocument:
        is_pdf = filename.lower().endswith(".pdf")

        if is_pdf:
            raw_text, tables, page_map = self._extract_pdf_pages_and_tables(file)
        else:
            raw_text = file.read().decode("utf-8", errors="replace")
            tables = []
            page_map = {1: raw_text}

        # 1. Parse Title, Authors, and Abstract
        title, authors, affiliations, abstract, body_text = self._extract_header_metadata(raw_text, filename)

        # 2. Parse Section Trees (H1, H2, H3)
        sections = self._extract_sections(body_text)

        # 3. Extract Bibliography References
        bibliography = self._extract_bibliography(sections, body_text)

        # 4. Extract Limitations & Methodology Summaries
        methodology_summary = self._summarize_section_type(sections, "methodology")
        limitations_summary = self._summarize_section_type(sections, "limitations")

        # 5. Build PaperStructure
        paper_id = str(uuid4())
        paper_struct = PaperStructure(
            id=paper_id,
            title=title,
            authors=authors,
            affiliations=affiliations,
            abstract=abstract,
            sections=sections,
            bibliography=bibliography,
            methodology_summary=methodology_summary,
            limitations_summary=limitations_summary,
            tables=tables,
            metadata={
                "filename": filename,
                "is_academic_paper": True,
                "section_count": len(sections),
                "reference_count": len(bibliography),
            },
        )

        full_content = paper_struct.to_markdown()

        return ParsedDocument(
            content=full_content,
            metadata={
                "format": "academic_paper",
                "filename": filename,
                "title": title,
                "authors": authors,
                "section_count": len(sections),
                "reference_count": len(bibliography),
                "has_limitations": bool(limitations_summary),
            },
            tables=tables,
            paper_structure=paper_struct,
            structure={
                "type": "academic_paper",
                "section_tree": [
                    {"id": s.section_id, "title": s.title, "type": s.section_type, "level": s.level}
                    for s in sections
                ],
            },
        )

    def _extract_pdf_pages_and_tables(self, file: BinaryIO) -> Tuple[str, List[Table], Dict[int, str]]:
        """Extract text and tables from PDF pages using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            # Fallback to plain read if pdfplumber is unavailable
            content = file.read().decode("utf-8", errors="replace")
            return content, [], {1: content}

        content_parts: List[str] = []
        tables: List[Table] = []
        page_map: Dict[int, str] = {}

        try:
            with pdfplumber.open(file) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    page_map[page_num] = text
                    if text.strip():
                        content_parts.append(text.strip())

                    # Extract tables
                    try:
                        page_tables = page.extract_tables()
                        for t_idx, t_data in enumerate(page_tables or []):
                            if t_data and len(t_data) > 1:
                                headers = [str(c).strip() if c else "" for c in t_data[0]]
                                rows = [[str(c).strip() if c else "" for c in r] for r in t_data[1:]]
                                tables.append(
                                    Table(
                                        id=str(uuid4()),
                                        headers=headers,
                                        rows=rows,
                                        page_number=page_num,
                                        caption=f"Table {t_idx + 1} (Page {page_num})",
                                    )
                                )
                    except Exception:
                        pass
            return "\n\n".join(content_parts), tables, page_map
        except Exception as e:
            logger.warning("Failed PDF extraction in AcademicPaperParser, falling back", error=str(e))
            file.seek(0)
            text = file.read().decode("utf-8", errors="replace")
            return text, [], {1: text}

    def _extract_header_metadata(self, text: str, filename: str) -> Tuple[str, List[str], List[str], str, str]:
        """Extract paper title, authors, affiliations, abstract, and remaining body text."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return filename, [], [], "", text

        title = lines[0]
        authors: List[str] = []
        affiliations: List[str] = []
        abstract = ""
        body_start_idx = 0

        # Detect Abstract boundary
        abstract_start = -1
        abstract_end = -1
        for idx, line in enumerate(lines[:30]):
            if re.match(r"^abstract\b", line, re.IGNORECASE):
                abstract_start = idx
                break

        if abstract_start != -1:
            # Authors are between title and abstract
            author_lines = lines[1:abstract_start]
            if author_lines:
                raw_authors = " ".join(author_lines)
                # Split authors by commas or 'and'
                authors = [a.strip() for a in re.split(r",|\band\b|;", raw_authors) if a.strip() and len(a.strip()) > 2][:8]

            # Find where abstract ends (typically next section header e.g. "1. Introduction" or "1 Introduction")
            for idx in range(abstract_start + 1, min(abstract_start + 25, len(lines))):
                if re.match(r"^(?:\d+\.?\s*)?(?:introduction|keywords|1\s+introduction)\b", lines[idx], re.IGNORECASE):
                    abstract_end = idx
                    break

            if abstract_end == -1:
                abstract_end = min(abstract_start + 10, len(lines))

            abstract_lines = lines[abstract_start:abstract_end]
            # Strip the leading "Abstract" word
            abstract_text = " ".join(abstract_lines)
            abstract = re.sub(r"^abstract[:\s-]*", "", abstract_text, flags=re.IGNORECASE).strip()
            body_start_idx = abstract_end
        else:
            # Fallback if no explicit Abstract keyword found
            title = lines[0]
            if len(lines) > 1 and len(lines[1]) < 100:
                authors = [a.strip() for a in lines[1].split(",") if a.strip()]
            body_start_idx = min(3, len(lines))

        body_text = "\n".join(lines[body_start_idx:])
        return title, authors, affiliations, abstract, body_text

    def _extract_sections(self, body_text: str) -> List[PaperSection]:
        """Hierarchically parse section headers and classify their structural type."""
        lines = body_text.split("\n")
        sections: List[PaperSection] = []
        current_title = "Introduction"
        current_type = "introduction"
        current_level = 1
        current_lines: List[str] = []

        header_regex = re.compile(
            r"^(?:(\d+(?:\.\d+)*)\.?\s+)?([A-Z][A-Za-z0-9\s,\-–:]{2,60})$"
        )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            match = header_regex.match(stripped)
            matched_type = self._classify_section(stripped)

            # Check if this line is a plausible section heading
            is_heading = False
            level = 1
            if matched_type != "other":
                is_heading = True
                level = 1
            elif match and len(stripped) < 60 and not stripped.endswith("."):
                num_prefix = match.group(1)
                if num_prefix:
                    is_heading = True
                    level = min(num_prefix.count(".") + 1, 3)

            if is_heading and current_lines:
                # Save previous section
                content_str = "\n".join(current_lines).strip()
                citations = self._find_citations(content_str)
                sections.append(
                    PaperSection(
                        section_id=str(uuid4()),
                        title=current_title,
                        level=current_level,
                        section_type=current_type,
                        content=content_str,
                        citations_referenced=citations,
                    )
                )
                current_title = stripped
                current_type = matched_type if matched_type != "other" else "other"
                current_level = level
                current_lines = []
            elif is_heading and not current_lines:
                current_title = stripped
                current_type = matched_type if matched_type != "other" else "other"
                current_level = level
            else:
                current_lines.append(stripped)

        # Flush final section
        if current_lines:
            content_str = "\n".join(current_lines).strip()
            citations = self._find_citations(content_str)
            sections.append(
                PaperSection(
                    section_id=str(uuid4()),
                    title=current_title,
                    level=current_level,
                    section_type=current_type,
                    content=content_str,
                    citations_referenced=citations,
                )
            )

        return sections

    def _classify_section(self, header_text: str) -> str:
        """Classify a section heading into standard academic taxonomy."""
        for sec_type, pattern in SECTION_PATTERNS:
            if pattern.search(header_text):
                return sec_type
        return "other"

    def _find_citations(self, text: str) -> List[str]:
        """Find all inline citation occurrences in text."""
        citations: List[str] = []
        for match in CITATION_REGEX.finditer(text):
            val = match.group(0)
            if val not in citations:
                citations.append(val)
        return citations

    def _extract_bibliography(self, sections: List[PaperSection], full_text: str) -> List[BibEntry]:
        """Extract and structure bibliographic citations from References section."""
        ref_sections = [s for s in sections if s.section_type == "references"]
        ref_text = ""
        if ref_sections:
            ref_text = "\n".join(s.content for s in ref_sections)
        else:
            # Fallback search for References block in text
            match = re.search(r"(?:references|bibliography)\s*\n(.*)", full_text, re.IGNORECASE | re.DOTALL)
            if match:
                ref_text = match.group(1)

        if not ref_text:
            return []

        entries: List[BibEntry] = []
        ref_lines = [l.strip() for l in ref_text.split("\n") if l.strip()]

        current_key = ""
        current_entry_parts: List[str] = []

        entry_start_regex = re.compile(r"^(?:\[(\d+)\]|(\d+)\.|\(([A-Za-z]+,\s*\d{4})\))\s*(.*)")

        for line in ref_lines:
            match = entry_start_regex.match(line)
            if match:
                if current_entry_parts:
                    raw_e = " ".join(current_entry_parts)
                    entries.append(self._build_bib_entry(current_key, raw_e))
                    current_entry_parts = []

                if match.group(1):
                    current_key = f"[{match.group(1)}]"
                elif match.group(2):
                    current_key = f"[{match.group(2)}]"
                elif match.group(3):
                    current_key = match.group(3)
                else:
                    current_key = f"[{len(entries) + 1}]"

                current_entry_parts.append(match.group(4) or line)
            else:
                current_entry_parts.append(line)

        if current_entry_parts:
            raw_e = " ".join(current_entry_parts)
            entries.append(self._build_bib_entry(current_key or f"[{len(entries) + 1}]", raw_e))

        return entries

    def _build_bib_entry(self, key: str, raw_text: str) -> BibEntry:
        """Parse raw citation text into structured BibEntry fields."""
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", raw_text)
        year = int(year_match.group(1)) if year_match else None

        doi_match = re.search(r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", raw_text, re.IGNORECASE)
        doi = doi_match.group(1) if doi_match else None

        arxiv_match = re.search(r"arXiv:(\d{4}\.\d{4,5})", raw_text, re.IGNORECASE)
        arxiv_id = arxiv_match.group(1) if arxiv_match else None

        return BibEntry(
            id=str(uuid4()),
            citation_key=key,
            raw_text=raw_text,
            year=year,
            doi=doi,
            arxiv_id=arxiv_id,
        )

    def _summarize_section_type(self, sections: List[PaperSection], target_type: str) -> str:
        """Aggregate content for a specific section type (e.g. methodology, limitations)."""
        matching = [s for s in sections if s.section_type == target_type]
        if not matching:
            return ""
        return "\n\n".join(f"### {s.title}\n{s.content}" for s in matching)
