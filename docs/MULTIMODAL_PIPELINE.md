# Multimodal Ingestion Pipeline

## Overview

The multimodal ingestion pipeline handles diverse input formats and normalizes them into a common internal representation for downstream processing.

## Pipeline Stages

```
Input → Detection → Parsing → Extraction → Normalization → Chunking → Embedding → Storage
```

### 1. Format Detection

```python
# packages/ingestion/detection.py
from enum import Enum
from pathlib import Path
import magic  # python-magic for MIME detection

class DocumentFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"
    HTML = "html"
    UNKNOWN = "unknown"

def detect_format(file_path: Path, mime_type: str | None = None) -> DocumentFormat:
    """Detect document format from file extension and MIME type."""
    suffix = file_path.suffix.lower()
    
    format_map = {
        ".txt": DocumentFormat.TEXT,
        ".md": DocumentFormat.MARKDOWN,
        ".markdown": DocumentFormat.MARKDOWN,
        ".pdf": DocumentFormat.PDF,
        ".docx": DocumentFormat.DOCX,
        ".png": DocumentFormat.IMAGE,
        ".jpg": DocumentFormat.IMAGE,
        ".jpeg": DocumentFormat.IMAGE,
        ".webp": DocumentFormat.IMAGE,
        ".html": DocumentFormat.HTML,
        ".htm": DocumentFormat.HTML,
    }
    
    if suffix in format_map:
        return format_map[suffix]
    
    # Fallback to MIME detection
    if mime_type:
        mime_map = {
            "text/plain": DocumentFormat.TEXT,
            "text/markdown": DocumentFormat.MARKDOWN,
            "application/pdf": DocumentFormat.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentFormat.DOCX,
            "image/png": DocumentFormat.IMAGE,
            "image/jpeg": DocumentFormat.IMAGE,
            "text/html": DocumentFormat.HTML,
        }
        if mime_type in mime_map:
            return mime_map[mime_type]
    
    return DocumentFormat.UNKNOWN
```

### 2. Parser Interface

```python
# packages/ingestion/parsers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from packages.ingestion.detection import DocumentFormat

@dataclass
class ParsedDocument:
    """Result of parsing a document."""
    content: str                    # Main text content
    metadata: dict                  # Format-specific metadata
    images: list["ImageRef"] = []   # Referenced images
    tables: list["Table"] = []      # Extracted tables
    structure: dict = {}            # Document structure (headings, sections)

@dataclass
class ImageRef:
    """Reference to an image in the document."""
    id: str
    data: bytes | None = None       # Image bytes (if embedded)
    path: str | None = None         # Path/URL if external
    mime_type: str = "image/png"
    caption: str | None = None
    page_number: int | None = None
    bbox: tuple[float, float, float, float] | None = None

@dataclass
class Table:
    """Extracted table data."""
    id: str
    headers: list[str]
    rows: list[list[str]]
    page_number: int | None = None
    caption: str | None = None
    format: str = "csv"  # csv, markdown, json

class DocumentParser(ABC):
    """Abstract base for document parsers."""
    
    @property
    @abstractmethod
    def supported_formats(self) -> list[DocumentFormat]:
        pass
    
    @abstractmethod
    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        pass
```

### 3. Concrete Parsers

```python
# packages/ingestion/parsers/text.py
from packages.ingestion.parsers.base import DocumentParser, ParsedDocument
from packages.ingestion.detection import DocumentFormat

class TextParser(DocumentParser):
    """Parse plain text and markdown files."""
    
    supported_formats = [DocumentFormat.TEXT, DocumentFormat.MARKDOWN]
    
    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        content = file.read().decode("utf-8")
        return ParsedDocument(
            content=content,
            metadata={"format": "text", "filename": filename},
        )

# packages/ingestion/parsers/pdf.py
import pdfplumber
from packages.ingestion.parsers.base import DocumentParser, ParsedDocument, ImageRef, Table
from packages.ingestion.detection import DocumentFormat
import uuid

class PDFParser(DocumentParser):
    """Parse PDF documents with text, tables, and images."""
    
    supported_formats = [DocumentFormat.PDF]
    
    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        # pdfplumber doesn't support async, run in thread pool
        import asyncio
        return await asyncio.to_thread(self._parse_sync, file, filename)
    
    def _parse_sync(self, file: BinaryIO, filename: str) -> ParsedDocument:
        content_parts = []
        images = []
        tables = []
        
        with pdfplumber.open(file) as pdf:
            metadata = {
                "format": "pdf",
                "filename": filename,
                "page_count": len(pdf.pages),
                "pdf_metadata": pdf.metadata or {},
            }
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                if text:
                    content_parts.append(f"[Page {page_num}]\n{text}")
                
                # Extract tables
                page_tables = page.extract_tables()
                for table_idx, table_data in enumerate(page_tables):
                    if table_data and len(table_data) > 1:
                        headers = [str(c) for c in table_data[0]]
                        rows = [[str(c) for c in row] for row in table_data[1:]]
                        tables.append(Table(
                            id=str(uuid.uuid4()),
                            headers=headers,
                            rows=rows,
                            page_number=page_num,
                        ))
                
                # Extract images (basic - pdfplumber limited)
                # For full image extraction, use PyMuPDF (fitz)
        
        return ParsedDocument(
            content="\n\n".join(content_parts),
            metadata=metadata,
            images=images,
            tables=tables,
        )

# packages/ingestion/parsers/image.py
from packages.ingestion.parsers.base import DocumentParser, ParsedDocument, ImageRef
from packages.ingestion.detection import DocumentFormat
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import VisionRequest
import base64
import uuid

class ImageParser(DocumentParser):
    """Parse images using vision models."""
    
    supported_formats = [DocumentFormat.IMAGE]
    
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
    
    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        image_data = file.read()
        mime_type = self._get_mime_type(filename)
        
        # Encode as base64 for vision model
        b64_image = base64.b64encode(image_data).decode()
        
        # Use vision model to describe image
        vision = self.router.select_vision()
        response = await vision.analyze(VisionRequest(
            images=[f"data:{mime_type};base64,{b64_image}"],
            prompt="Describe this image in detail. Extract any text, tables, charts, or structured data.",
        ))
        
        return ParsedDocument(
            content=response.content,
            metadata={"format": "image", "filename": filename, "mime_type": mime_type},
            images=[ImageRef(
                id=str(uuid.uuid4()),
                data=image_data,
                mime_type=mime_type,
            )],
        )
    
    def _get_mime_type(self, filename: str) -> str:
        ext = filename.lower().split(".")[-1]
        return {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }.get(ext, "image/png")

# packages/ingestion/parsers/docx.py
from docx import Document as DocxDocument
from packages.ingestion.parsers.base import DocumentParser, ParsedDocument, Table
from packages.ingestion.detection import DocumentFormat
import uuid

class DocxParser(DocumentParser):
    """Parse DOCX documents."""
    
    supported_formats = [DocumentFormat.DOCX]
    
    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        import asyncio
        return await asyncio.to_thread(self._parse_sync, file, filename)
    
    def _parse_sync(self, file: BinaryIO, filename: str) -> ParsedDocument:
        doc = DocxDocument(file)
        
        content_parts = []
        tables = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                content_parts.append(para.text)
        
        for table_idx, table in enumerate(doc.tables):
            rows = [[cell.text for cell in row.cells] for row in table.rows]
            if rows:
                headers = rows[0]
                data_rows = rows[1:]
                tables.append(Table(
                    id=str(uuid.uuid4()),
                    headers=headers,
                    rows=data_rows,
                ))
        
        return ParsedDocument(
            content="\n".join(content_parts),
            metadata={"format": "docx", "filename": filename},
            tables=tables,
        )
```

### 4. Parser Registry

```python
# packages/ingestion/parsers/registry.py
from packages.ingestion.parsers.base import DocumentParser
from packages.ingestion.detection import DocumentFormat, detect_format
from packages.ingestion.parsers.text import TextParser
from packages.ingestion.parsers.pdf import PDFParser
from packages.ingestion.parsers.image import ImageParser
from packages.ingestion.parsers.docx import DocxParser
from packages.ai.providers.router import ModelRouter

class ParserRegistry:
    """Registry for document parsers."""
    
    def __init__(self, model_router: ModelRouter | None = None):
        self._parsers: list[DocumentParser] = [
            TextParser(),
            PDFParser(),
            DocxParser(),
        ]
        if model_router:
            self._parsers.append(ImageParser(model_router))
    
    def get_parser(self, format: DocumentFormat) -> DocumentParser | None:
        for parser in self._parsers:
            if format in parser.supported_formats:
                return parser
        return None
    
    async def parse(self, file: BinaryIO, filename: str, mime_type: str | None = None) -> ParsedDocument:
        format = detect_format(filename, mime_type)
        parser = self.get_parser(format)
        if not parser:
            raise ValueError(f"No parser for format: {format}")
        return await parser.parse(file, filename)
```

### 5. Chunking Strategies

```python
# packages/ingestion/chunking.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from packages.ingestion.parsers.base import ParsedDocument

@dataclass
class Chunk:
    """A semantic chunk of a document."""
    id: str
    content: str
    metadata: dict
    start_char: int
    end_char: int
    chunk_index: int

class ChunkingStrategy(ABC):
    """Abstract chunking strategy."""
    
    @abstractmethod
    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        pass

class FixedSizeChunker(ChunkingStrategy):
    """Fixed-size overlapping chunks."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        chunks = []
        text = document.content
        start = 0
        index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunks.append(Chunk(
                id=f"{document.metadata.get('filename', 'doc')}_{index}",
                content=chunk_text,
                metadata={**document.metadata, "chunk_index": index},
                start_char=start,
                end_char=end,
                chunk_index=index,
            ))
            
            start = end - self.overlap
            index += 1
        
        return chunks

class SemanticChunker(ChunkingStrategy):
    """Semantic chunking using headings/structure."""
    
    def __init__(self, max_chunk_size: int = 2000):
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        # Split by headings, paragraphs, sections
        # For MVP, use simple paragraph-based chunking
        paragraphs = document.content.split("\n\n")
        
        chunks = []
        current_chunk = ""
        current_start = 0
        index = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > self.max_chunk_size and current_chunk:
                chunks.append(Chunk(
                    id=f"{document.metadata.get('filename', 'doc')}_{index}",
                    content=current_chunk.strip(),
                    metadata={**document.metadata, "chunk_index": index},
                    start_char=current_start,
                    end_char=current_start + len(current_chunk),
                    chunk_index=index,
                ))
                current_start += len(current_chunk)
                current_chunk = ""
                index += 1
            
            current_chunk += para + "\n\n"
        
        if current_chunk:
            chunks.append(Chunk(...))
        
        return chunks
```

### 6. Ingestion Pipeline

```python
# packages/ingestion/pipeline.py
from packages.ingestion.parsers.registry import ParserRegistry
from packages.ingestion.chunking import ChunkingStrategy, SemanticChunker
from packages.ingestion.parsers.base import ParsedDocument
from packages.retrieval.embedder import Embedder
from packages.retrieval.vector_store import VectorStore
from packages.database.repositories import DocumentRepository
from packages.database.models import Document, DocumentChunk
import uuid

class IngestionPipeline:
    """Orchestrates the full ingestion pipeline."""
    
    def __init__(
        self,
        parser_registry: ParserRegistry,
        chunker: ChunkingStrategy,
        embedder: Embedder,
        vector_store: VectorStore,
        doc_repo: DocumentRepository,
    ):
        self.parsers = parser_registry
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.doc_repo = doc_repo
    
    async def ingest(
        self,
        file: BinaryIO,
        filename: str,
        mime_type: str | None = None,
        research_job_id: str | None = None,
    ) -> Document:
        """Ingest a document through the full pipeline."""
        
        # 1. Parse
        parsed = await self.parsers.parse(file, filename, mime_type)
        
        # 2. Create document record
        doc = Document(
            id=str(uuid.uuid4()),
            filename=filename,
            mime_type=mime_type or "application/octet-stream",
            content=parsed.content,
            metadata=parsed.metadata,
            research_job_id=research_job_id,
        )
        await self.doc_repo.create(doc)
        
        # 3. Chunk
        chunks = self.chunker.chunk(parsed)
        
        # 4. Embed
        chunk_texts = [c.content for c in chunks]
        embeddings = await self.embedder.embed(chunk_texts)
        
        # 5. Store chunks with embeddings
        chunk_records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_record = DocumentChunk(
                id=chunk.id,
                document_id=doc.id,
                content=chunk.content,
                embedding=embedding,
                metadata={**chunk.metadata, "start_char": chunk.start_char, "end_char": chunk.end_char},
                chunk_index=i,
            )
            chunk_records.append(chunk_record)
        
        await self.doc_repo.create_chunks(chunk_records)
        await self.vector_store.add(chunk_records)
        
        return doc
```

## Normalized Internal Representation

All parsed documents convert to `ParsedDocument` with:
- `content`: Extracted text (primary for embedding/search)
- `metadata`: Format-specific info (page count, author, etc.)
- `images`: List of `ImageRef` with data/paths
- `tables`: List of `Table` with headers/rows
- `structure`: Headings, sections for semantic chunking

Downstream agents only need to understand `ParsedDocument`, not original formats.

---

*Pipeline is extensible: add new parsers by implementing `DocumentParser` and registering.*