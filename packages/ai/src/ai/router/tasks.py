"""Task definitions and capability mappings for routing."""

from enum import Enum
from typing import Dict, Set, Union
from ai.schemas import ModelCapability


class TaskType(str, Enum):
    """Standard task types for capability-based routing."""

    FAST_TEXT = "fast_text_generation"
    DEEP_REASONING = "deep_reasoning"
    VISION_ANALYSIS = "vision_analysis"
    LONG_FORM_RESEARCH = "long_form_research"
    STREAMING_RESPONSE = "streaming_response"
    PLANNING = "planning"
    SYNTHESIS = "synthesis"
    REPORT = "report"


# Canonical task aliases mapping human-friendly phrases to standard TaskType
TASK_ALIASES: Dict[str, TaskType] = {
    "fast text generation": TaskType.FAST_TEXT,
    "fast_text_generation": TaskType.FAST_TEXT,
    "fast": TaskType.FAST_TEXT,
    "deep reasoning": TaskType.DEEP_REASONING,
    "deep_reasoning": TaskType.DEEP_REASONING,
    "reasoning": TaskType.DEEP_REASONING,
    "vision analysis": TaskType.VISION_ANALYSIS,
    "vision_analysis": TaskType.VISION_ANALYSIS,
    "vision": TaskType.VISION_ANALYSIS,
    "long-form research": TaskType.LONG_FORM_RESEARCH,
    "long_form_research": TaskType.LONG_FORM_RESEARCH,
    "research": TaskType.LONG_FORM_RESEARCH,
    "streaming response": TaskType.STREAMING_RESPONSE,
    "streaming_response": TaskType.STREAMING_RESPONSE,
    "streaming": TaskType.STREAMING_RESPONSE,
    "planning": TaskType.PLANNING,
    "synthesis": TaskType.SYNTHESIS,
    "report": TaskType.REPORT,
}

# Task to required capabilities mapping
TASK_REQUIRED_CAPABILITIES: Dict[TaskType, Set[ModelCapability]] = {
    TaskType.FAST_TEXT: {ModelCapability.SUMMARIZATION},
    TaskType.DEEP_REASONING: {ModelCapability.REASONING},
    TaskType.VISION_ANALYSIS: {ModelCapability.VISION, ModelCapability.EXTRACTION},
    TaskType.LONG_FORM_RESEARCH: {ModelCapability.REASONING, ModelCapability.EXTRACTION, ModelCapability.SUMMARIZATION},
    TaskType.STREAMING_RESPONSE: {ModelCapability.REASONING},
    TaskType.PLANNING: {ModelCapability.REASONING, ModelCapability.TOOL_USE},
    TaskType.SYNTHESIS: {ModelCapability.REASONING, ModelCapability.SUMMARIZATION},
    TaskType.REPORT: {ModelCapability.SUMMARIZATION, ModelCapability.JSON_MODE},
}


def normalize_task(task: Union[str, TaskType]) -> TaskType:
    """Normalize a task string or enum into a canonical TaskType."""
    if isinstance(task, TaskType):
        return task
    cleaned = task.strip().lower()
    if cleaned in TASK_ALIASES:
        return TASK_ALIASES[cleaned]
    try:
        return TaskType(cleaned)
    except ValueError:
        # Default to fast text if unrecognized
        return TaskType.FAST_TEXT


def get_required_capabilities(task: Union[str, TaskType]) -> Set[ModelCapability]:
    """Get the set of required model capabilities for a given task."""
    task_type = normalize_task(task)
    return TASK_REQUIRED_CAPABILITIES.get(task_type, {ModelCapability.REASONING})
