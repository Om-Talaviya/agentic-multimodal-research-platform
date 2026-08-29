"""AI provider schemas and data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any
from enum import Enum
from shared.types import JSONDict


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ModelCapability(str, Enum):
    REASONING = "reasoning"
    CODING = "coding"
    SUMMARIZATION = "summarization"
    VISION = "vision"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    TOOL_USE = "tool_use"
    JSON_MODE = "json_mode"
    EMBEDDING = "embedding"


class ModelCapabilities(frozenset[ModelCapability]):
    """Immutable set of required capabilities."""
    
    @classmethod
    def for_task(cls, task_type: str) -> "ModelCapabilities":
        """Get required capabilities for a task type."""
        task_map = {
            "planning": {ModelCapability.REASONING, ModelCapability.TOOL_USE},
            "research": {ModelCapability.REASONING, ModelCapability.EXTRACTION},
            "synthesis": {ModelCapability.REASONING, ModelCapability.SUMMARIZATION},
            "report": {ModelCapability.SUMMARIZATION, ModelCapability.JSON_MODE},
            "vision": {ModelCapability.VISION, ModelCapability.EXTRACTION},
            "embedding": {ModelCapability.EMBEDDING},
            "rerank": {ModelCapability.CLASSIFICATION},
        }
        return cls(task_map.get(task_type, {ModelCapability.REASONING}))


class LLMMessage(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None


class LLMRequest(BaseModel):
    messages: List[LLMMessage]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    json_mode: bool = False
    tools: Optional[List[dict]] = None
    tool_choice: Optional[Literal["auto", "none", "required"]] = "auto"
    metadata: JSONDict = Field(default_factory=dict)


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None
    tool_calls: Optional[List[dict]] = None
    finish_reason: Optional[str] = None
    metadata: JSONDict = Field(default_factory=dict)


class VisionRequest(BaseModel):
    images: List[str]  # Base64 data URLs or HTTP URLs
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    metadata: JSONDict = Field(default_factory=dict)


class VisionResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None
    metadata: JSONDict = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = None
    metadata: JSONDict = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    usage: Optional[dict] = None
    dimensions: Optional[int] = None
    metadata: JSONDict = Field(default_factory=dict)


class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    model: Optional[str] = None
    top_k: int = 10
    metadata: JSONDict = Field(default_factory=dict)


class RerankResponse(BaseModel):
    results: List[dict]  # {index, score, document}
    model: str
    usage: Optional[dict] = None
    metadata: JSONDict = Field(default_factory=dict)


class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str
    provider: str
    capabilities: List[ModelCapability] = Field(default_factory=list)
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    is_local: bool = False
    metadata: JSONDict = Field(default_factory=dict)


class ProviderHealth(BaseModel):
    """Provider health status."""
    provider: str
    healthy: bool
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    models: List[ModelInfo] = Field(default_factory=list)