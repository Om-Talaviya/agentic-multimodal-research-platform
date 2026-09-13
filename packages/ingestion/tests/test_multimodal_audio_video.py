"""Unit tests for Phase 12 Advanced Multimodal Research (Audio, Video, Charts, Multimodal Chunking)."""

import io
import pytest
from ingestion.chunking import SemanticChunker
from ingestion.detection import detect_format
from ingestion.parsers.audio import AudioParser
from ingestion.parsers.base import AudioSegment, ChartRef, ImageRef, ParsedDocument
from ingestion.parsers.image import ImageParser
from ingestion.parsers.registry import ParserRegistry
from ingestion.parsers.video import VideoParser
from shared.types import DocumentFormat


@pytest.mark.asyncio
async def test_audio_format_detection():
    assert detect_format("interview.mp3", "audio/mpeg") == DocumentFormat.AUDIO
    assert detect_format("lecture.wav", "audio/wav") == DocumentFormat.AUDIO
    assert detect_format("podcast.m4a", "audio/mp4") == DocumentFormat.AUDIO
    assert detect_format("audio.flac", "audio/flac") == DocumentFormat.AUDIO


@pytest.mark.asyncio
async def test_video_format_detection():
    assert detect_format("presentation.mp4", "video/mp4") == DocumentFormat.VIDEO
    assert detect_format("demo.mov", "video/quicktime") == DocumentFormat.VIDEO
    assert detect_format("webinar.webm", "video/webm") == DocumentFormat.VIDEO


@pytest.mark.asyncio
async def test_audio_parser_fallback_and_segments():
    parser = AudioParser()
    audio_bytes = b"ID3" + b"\x00" * 1024
    fake_file = io.BytesIO(audio_bytes)

    parsed = await parser.parse(fake_file, "keynote_speech.mp3")

    assert parsed.metadata["format"] == "audio"
    assert parsed.metadata["filename"] == "keynote_speech.mp3"
    assert len(parsed.audio_segments) >= 1
    first_seg = parsed.audio_segments[0]
    assert first_seg.start_seconds >= 0.0
    assert first_seg.end_seconds > first_seg.start_seconds
    assert "Audio" in parsed.content


@pytest.mark.asyncio
async def test_audio_parser_segment_parsing_logic():
    parser = AudioParser()
    raw_transcript = (
        "[00:00 - 00:15] Alice: Welcome everyone to the multimodal AI symposium.\n"
        "[00:15 - 01:20] Bob: In this session, we present our findings on video grounding.\n"
        "[01:20 - 02:45] Alice: Let's examine the benchmark results."
    )
    segments = parser._extract_segments_from_text(raw_transcript)

    assert len(segments) == 3
    assert segments[0].speaker == "Alice"
    assert segments[0].start_seconds == 0.0
    assert segments[0].end_seconds == 15.0
    assert "Welcome everyone" in segments[0].text

    assert segments[1].speaker == "Bob"
    assert segments[1].start_seconds == 15.0
    assert segments[1].end_seconds == 80.0

    assert segments[2].start_seconds == 80.0
    assert segments[2].end_seconds == 165.0


@pytest.mark.asyncio
async def test_video_parser_multimodal_timeline():
    parser = VideoParser()
    video_bytes = b"\x00\x00\x00 ftypmp42" + b"\x00" * 4096
    fake_file = io.BytesIO(video_bytes)

    parsed = await parser.parse(fake_file, "model_demo.mp4")

    assert parsed.metadata["format"] == "video"
    assert len(parsed.images) >= 1
    assert parsed.images[0].metadata["type"] == "keyframe_thumbnail"
    assert len(parsed.audio_segments) >= 1
    assert "Timeline" in parsed.content or "Video" in parsed.content


@pytest.mark.asyncio
async def test_image_parser_chart_extraction():
    parser = ImageParser()
    fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 512)

    # Filename contains chart cue
    parsed = await parser.parse(fake_img, "system_throughput_bar_chart.png")

    assert parsed.metadata["format"] == "image"
    assert parsed.metadata["has_charts"] is True
    assert len(parsed.charts) == 1
    chart = parsed.charts[0]
    assert chart.chart_type == "bar_chart"
    assert "system_throughput_bar_chart" in chart.title
    assert "Chart:" in chart.to_markdown()


@pytest.mark.asyncio
async def test_multimodal_semantic_chunker():
    chunker = SemanticChunker()

    audio_doc = ParsedDocument(
        content="Ignored when segments present",
        metadata={"filename": "interview.mp3", "format": "audio"},
        audio_segments=[
            AudioSegment(start_seconds=0.0, end_seconds=30.0, text="Introductory remarks.", speaker="Alice"),
            AudioSegment(start_seconds=30.0, end_seconds=90.0, text="Detailed discussion.", speaker="Bob"),
        ],
    )

    chunks = chunker.chunk(audio_doc)
    assert len(chunks) == 2
    assert chunks[0].metadata["chunk_type"] == "audio_segment"
    assert chunks[0].metadata["timestamp_start"] == 0.0
    assert chunks[0].metadata["timestamp_end"] == 30.0
    assert chunks[0].metadata["speaker"] == "Alice"
    assert "[00:00 - 00:30] (Alice): Introductory remarks." in chunks[0].content

    assert chunks[1].metadata["timestamp_start"] == 30.0
    assert chunks[1].metadata["timestamp_end"] == 90.0


@pytest.mark.asyncio
async def test_chart_semantic_chunker():
    chunker = SemanticChunker()

    chart_doc = ParsedDocument(
        content="Scientific paper paragraph text discussing model scaling laws.",
        metadata={"filename": "paper_figure.png", "format": "image"},
        charts=[
            ChartRef(
                id="chart-1",
                chart_type="scatter_plot",
                title="Model Accuracy vs Parameters",
                data_series={"7B": 74.2, "13B": 81.5, "70B": 89.1},
                summary="Parameters show log-linear scaling with accuracy.",
            )
        ],
    )

    chunks = chunker.chunk(chart_doc)
    assert len(chunks) >= 2
    chart_chunk = next(c for c in chunks if c.metadata.get("chunk_type") == "chart_series")
    assert chart_chunk.metadata["chart_type"] == "scatter_plot"
    assert chart_chunk.metadata["chart_data"]["70B"] == 89.1
    assert "Model Accuracy vs Parameters" in chart_chunk.content


@pytest.mark.asyncio
async def test_parser_registry_multimodal_dispatch():
    registry = ParserRegistry()

    assert registry.get_parser(DocumentFormat.AUDIO) is not None
    assert registry.get_parser(DocumentFormat.VIDEO) is not None
    assert registry.get_parser(DocumentFormat.IMAGE) is not None

    audio_res = await registry.parse(io.BytesIO(b"audio"), "podcast.mp3")
    assert audio_res.metadata["format"] == "audio"

    video_res = await registry.parse(io.BytesIO(b"video"), "demo.mp4")
    assert video_res.metadata["format"] == "video"
