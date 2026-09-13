"""Tests for image parser."""

import io
from unittest.mock import AsyncMock, MagicMock
import pytest
from ai.gateway.model_gateway import ModelGateway
from ai.schemas import VisionResponse
from ingestion.parsers.image import ImageParser
from shared.types import DocumentFormat


@pytest.mark.asyncio
async def test_image_parser_with_gateway():
    mock_gateway = MagicMock(spec=ModelGateway)
    mock_gateway.analyze_vision = AsyncMock(
        return_value=VisionResponse(
            content="A chart showing quantum algorithm performance with 98% accuracy.",
            model="gemini-2.0-flash",
        )
    )

    parser = ImageParser(vision_source=mock_gateway)
    assert DocumentFormat.IMAGE in parser.supported_formats

    image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRdummy"
    file_obj = io.BytesIO(image_data)

    parsed = await parser.parse(file_obj, "chart.png")

    assert "A chart showing quantum algorithm performance" in parsed.content
    assert parsed.metadata["format"] == "image"
    assert parsed.metadata["mime_type"] == "image/png"
    assert parsed.metadata["model"] == "gemini-2.0-flash"
    assert len(parsed.images) == 1
    assert parsed.images[0].data == image_data
    assert parsed.images[0].mime_type == "image/png"
    assert mock_gateway.analyze_vision.await_count == 1


@pytest.mark.asyncio
async def test_image_parser_without_vision_source():
    parser = ImageParser(vision_source=None)
    file_obj = io.BytesIO(b"fakejpeg")

    parsed = await parser.parse(file_obj, "photo.jpg")
    assert "[Image: photo.jpg]" in parsed.content
    assert parsed.metadata["mime_type"] == "image/jpeg"
    assert len(parsed.images) == 1
