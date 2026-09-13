"""Unit tests for agent tracing."""

from datetime import UTC, datetime, timedelta
import pytest
from agents.tracing import AgentTrace, ToolCallTrace, ModelCallTrace


def test_tool_call_trace_serialization():
    tc = ToolCallTrace(
        tool_name="web_fetch",
        arguments={"url": "https://example.com"},
        output="Extracted web text",
        success=True,
        duration_ms=150,
    )
    d = tc.to_dict()
    assert d["tool_name"] == "web_fetch"
    assert d["success"] is True
    assert d["duration_ms"] == 150
    assert "timestamp" in d


def test_model_call_trace_serialization():
    mc = ModelCallTrace(
        provider="gemini",
        model="gemini-2.0-flash",
        request_type="complete",
        prompt_tokens=500,
        completion_tokens=150,
        total_tokens=650,
        latency_ms=800,
    )
    d = mc.to_dict()
    assert d["provider"] == "gemini"
    assert d["total_tokens"] == 650
    assert d["latency_ms"] == 800


def test_agent_trace_lifecycle_and_duration():
    trace = AgentTrace(
        agent_name="web_research",
        task_id="task_123",
        job_id="job_456",
        request_id="req_789",
        input={"query": "multimodal AI"},
    )
    trace.add_tool_call(ToolCallTrace("web_search", {"query": "AI"}, output=[], duration_ms=100))
    trace.add_model_call(ModelCallTrace("ollama", "qwen2.5:7b", prompt_tokens=100, completion_tokens=50))

    # Fast forward start time to test duration
    trace.started_at = datetime.now(UTC) - timedelta(seconds=2)
    trace.complete(success=True, output={"status": "done"})

    assert trace.success is True
    assert trace.duration_ms >= 1900
    assert len(trace.tool_calls) == 1
    assert len(trace.model_calls) == 1

    d = trace.to_dict()
    assert d["agent_name"] == "web_research"
    assert d["completed_at"] is not None
    assert len(d["tool_calls"]) == 1
