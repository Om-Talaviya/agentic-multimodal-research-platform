"""Unit tests for PresentationGenerator and PodcastBriefingSynthesizer."""

import pytest
from research.presentation.synthesizer import (
    PresentationGenerator,
    PodcastBriefingSynthesizer,
)


def test_presentation_generator_deck_structure():
    """Verify structured slide deck generation with notes and metadata."""
    deck = PresentationGenerator.generate_deck_from_research(
        title="Zero-Noise Extrapolation in Quantum Processors",
        research_content="Empirical validation shows 34% fidelity enhancement across 16 superconducting qubits.",
        target_audience="executive",
        theme="obsidian_glow",
    )

    assert deck["title"] == "Zero-Noise Extrapolation in Quantum Processors"
    assert deck["target_audience"] == "executive"
    assert deck["total_slides"] == 5
    assert len(deck["slides"]) == 5

    # Check slide 1 (Title) and slide 2 (Summary)
    assert deck["slides"][0]["layout_type"] == "title"
    assert deck["slides"][1]["layout_type"] == "bullet_points"
    assert len(deck["slides"][0]["bullet_points"]) >= 1
    assert "speaker_notes" in deck["slides"][0]
    assert len(deck["slides"][0]["speaker_notes"]) > 0


def test_podcast_briefing_synthesizer():
    """Verify multi-speaker dialogue synthesis with timestamps and acoustic cues."""
    podcast = PodcastBriefingSynthesizer.generate_podcast_dialogue(
        topic="Solid-State Lithium Batteries",
        key_findings="450 Wh/kg achieved with zero thermal runaway in 2026 trials.",
        host_name="Dr. Elena Vance (Host)",
        expert_name="Prof. Marcus Sterling (Specialist)",
    )

    assert podcast["episode_topic"] == "Solid-State Lithium Batteries"
    assert podcast["total_duration_sec"] > 0
    assert podcast["total_dialogue_turns"] >= 5
    assert len(podcast["dialogue_transcript_json"]) == podcast["total_dialogue_turns"]

    first_turn = podcast["dialogue_transcript_json"][0]
    assert first_turn["speaker"] == "Dr. Elena Vance (Host)"
    assert first_turn["timestamp_start_sec"] == 0.0
    assert first_turn["timestamp_end_sec"] > 0.0
    assert "audio_cue" in first_turn
