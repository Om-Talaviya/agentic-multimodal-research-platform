"""Model registry and model metadata definitions."""
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, ConfigDict, Field

from ai.schemas import ModelCapability
from shared.types import JSONDict


class ModelDefinition(BaseModel):
    """Complete metadata definition for an AI model."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    model_id: str
    provider_name: str
    capabilities: Set[ModelCapability] = Field(default_factory=set)
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    supports_streaming: bool = True
    supports_vision: bool = False
    task_suitability: List[str] = Field(default_factory=list)
    priority: int = 10  # Higher priority is preferred in capability routing
    is_local: bool = True
    metadata: JSONDict = Field(default_factory=dict)

    # Phase 8A: Cost and tier metadata
    tier: str = "paid"  # "free" or "paid" — configurable per model
    input_cost: float = 0.0  # Cost per 1K input tokens (in USD or platform units)
    output_cost: float = 0.0  # Cost per 1K output tokens (in USD or platform units)

    def is_free(self) -> bool:
        """Check if this model is configured as free tier."""
        return self.tier == "free"

    def is_paid(self) -> bool:
        """Check if this model is configured as paid tier."""
        return self.tier == "paid"

    def estimated_cost(self, input_tokens: int = 0, output_tokens: int = 0) -> float:
        """Estimate cost for a generation request."""
        return (
            (self.input_cost / 1000) * input_tokens
            + (self.output_cost / 1000) * output_tokens
        )


class ModelRegistry:
    """Central registry of all available AI model definitions."""

    def __init__(self) -> None:
        self._models: Dict[str, ModelDefinition] = {}

    def register(self, model: ModelDefinition) -> None:
        """Register or update a model definition."""
        self._models[model.model_id] = model

    def unregister(self, model_id: str) -> bool:
        """Remove a model from the registry."""
        if model_id in self._models:
            del self._models[model_id]
            return True
        return False

    def get(self, model_id: str) -> Optional[ModelDefinition]:
        """Get model definition by model ID."""
        return self._models.get(model_id)

    def contains(self, model_id: str) -> bool:
        """Check if model exists in registry."""
        return model_id in self._models

    def list_models(
        self,
        provider_name: Optional[str] = None,
        capability: Optional[ModelCapability] = None,
        task: Optional[str] = None,
        supports_vision: Optional[bool] = None,
        supports_streaming: Optional[bool] = None,
        tier: Optional[str] = None,  # NEW: filter by free/paid
    ) -> List[ModelDefinition]:
        """List registered models matching given filters, ordered by priority descending.

        Args:
            provider_name: Filter by provider
            capability: Filter by required capability
            task: Filter by task suitability
            supports_vision: Filter by vision support
            supports_streaming: Filter by streaming support
            tier: Filter by "free" or "paid" tier

        Returns:
            List of ModelDefinition ordered by priority descending
        """
        results = list(self._models.values())

        if provider_name is not None:
            results = [m for m in results if m.provider_name == provider_name]

        if capability is not None:
            results = [m for m in results if capability in m.capabilities]

        if task is not None:
            results = [m for m in results if task in m.task_suitability]

        if supports_vision is not None:
            results = [m for m in results if m.supports_vision == supports_vision]

        if supports_streaming is not None:
            results = [m for m in results if m.supports_streaming == supports_streaming]

        if tier is not None:
            results = [m for m in results if m.tier == tier]

        # Order by priority descending, then model_id ascending
        return sorted(results, key=lambda m: (-m.priority, m.model_id))

    def clear(self) -> None:
        """Clear all registered models."""
        self._models.clear()