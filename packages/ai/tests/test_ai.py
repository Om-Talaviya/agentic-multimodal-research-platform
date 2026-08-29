"""Tests for AI package."""

import pytest
from ai.schemas import (
    LLMMessage, LLMRequest, LLMResponse,
    VisionRequest, VisionResponse,
    EmbeddingRequest, EmbeddingResponse,
    ModelCapability, ModelCapabilities,
    MessageRole,
)


def test_model_capabilities_for_task():
    """Test ModelCapabilities.for_task returns correct capabilities."""
    planning_caps = ModelCapabilities.for_task("planning")
    assert ModelCapability.REASONING in planning_caps
    assert ModelCapability.TOOL_USE in planning_caps
    
    research_caps = ModelCapabilities.for_task("research")
    assert ModelCapability.REASONING in research_caps
    assert ModelCapability.EXTRACTION in research_caps
    
    embedding_caps = ModelCapabilities.for_task("embedding")
    assert ModelCapability.EMBEDDING in embedding_caps
    
    # Unknown task defaults to reasoning
    unknown_caps = ModelCapabilities.for_task("unknown")
    assert ModelCapability.REASONING in unknown_caps


def test_llm_message():
    """Test LLMMessage model."""
    msg = LLMMessage(role=MessageRole.USER, content="Hello")
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello"
    assert msg.name is None
    
    msg_with_name = LLMMessage(role=MessageRole.ASSISTANT, content="Hi", name="assistant")
    assert msg_with_name.name == "assistant"


def test_llm_request():
    """Test LLMRequest model."""
    request = LLMRequest(
        messages=[LLMMessage(role=MessageRole.USER, content="Hello")],
        model="llama3.1",
        temperature=0.5,
        json_mode=True,
    )
    
    assert len(request.messages) == 1
    assert request.model == "llama3.1"
    assert request.temperature == 0.5
    assert request.json_mode is True
    assert request.tools is None


def test_llm_response():
    """Test LLMResponse model."""
    response = LLMResponse(
        content="Hello there!",
        model="llama3.1",
        usage={"prompt_tokens": 10, "completion_tokens": 5},
        finish_reason="stop",
    )
    
    assert response.content == "Hello there!"
    assert response.model == "llama3.1"
    assert response.usage["prompt_tokens"] == 10


def test_vision_request():
    """Test VisionRequest model."""
    request = VisionRequest(
        images=["data:image/png;base64,abc123"],
        prompt="Describe this image",
        model="llava",
    )
    
    assert len(request.images) == 1
    assert request.prompt == "Describe this image"
    assert request.model == "llava"


def test_embedding_request():
    """Test EmbeddingRequest model."""
    request = EmbeddingRequest(
        texts=["text one", "text two"],
        model="nomic-embed-text",
    )
    
    assert len(request.texts) == 2
    assert request.model == "nomic-embed-text"


def test_embedding_response():
    """Test EmbeddingResponse model."""
    response = EmbeddingResponse(
        embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        model="nomic-embed-text",
        dimensions=3,
    )
    
    assert len(response.embeddings) == 2
    assert len(response.embeddings[0]) == 3
    assert response.dimensions == 3


def test_model_capabilities_operations():
    """Test ModelCapabilities set operations."""
    caps1 = ModelCapabilities({ModelCapability.REASONING, ModelCapability.CODING})
    caps2 = ModelCapabilities({ModelCapability.REASONING})
    
    assert caps2.issubset(caps1)
    assert not caps1.issubset(caps2)
    assert ModelCapability.REASONING in caps1
    assert ModelCapability.VISION not in caps1