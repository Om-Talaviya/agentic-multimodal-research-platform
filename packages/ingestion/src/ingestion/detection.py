"""Format detection for documents and media."""

from pathlib import Path
from typing import Optional, Union
from shared.types import DocumentFormat

# Mapping from file extensions to DocumentFormat
EXTENSION_FORMAT_MAP: dict[str, DocumentFormat] = {
    ".txt": DocumentFormat.TEXT,
    ".text": DocumentFormat.TEXT,
    ".md": DocumentFormat.MARKDOWN,
    ".markdown": DocumentFormat.MARKDOWN,
    ".pdf": DocumentFormat.PDF,
    ".docx": DocumentFormat.DOCX,
    ".png": DocumentFormat.IMAGE,
    ".jpg": DocumentFormat.IMAGE,
    ".jpeg": DocumentFormat.IMAGE,
    ".webp": DocumentFormat.IMAGE,
    ".gif": DocumentFormat.IMAGE,
    ".bmp": DocumentFormat.IMAGE,
    ".html": DocumentFormat.HTML,
    ".htm": DocumentFormat.HTML,
}

# Fallback mapping from MIME types to DocumentFormat
MIME_FORMAT_MAP: dict[str, DocumentFormat] = {
    "text/plain": DocumentFormat.TEXT,
    "text/markdown": DocumentFormat.MARKDOWN,
    "text/x-markdown": DocumentFormat.MARKDOWN,
    "application/pdf": DocumentFormat.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentFormat.DOCX,
    "application/msword": DocumentFormat.DOCX,
    "image/png": DocumentFormat.IMAGE,
    "image/jpeg": DocumentFormat.IMAGE,
    "image/webp": DocumentFormat.IMAGE,
    "image/gif": DocumentFormat.IMAGE,
    "image/bmp": DocumentFormat.IMAGE,
    "text/html": DocumentFormat.HTML,
}


def detect_format(file_path: Union[str, Path], mime_type: Optional[str] = None) -> DocumentFormat:
    """Detect document format from file extension and optional MIME type."""
    path = Path(file_path) if isinstance(file_path, str) else file_path
    suffix = path.suffix.lower()

    if suffix in EXTENSION_FORMAT_MAP:
        return EXTENSION_FORMAT_MAP[suffix]

    if mime_type:
        clean_mime = mime_type.split(";")[0].strip().lower()
        if clean_mime in MIME_FORMAT_MAP:
            return MIME_FORMAT_MAP[clean_mime]

    return DocumentFormat.UNKNOWN
