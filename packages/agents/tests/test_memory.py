"""Unit tests for AgentMemory."""

import pytest
from agents.memory import AgentMemory, MemoryItem


def test_short_term_memory_bounded():
    memory = AgentMemory(max_short_term=3)

    memory.add_short_term("user", "Hello 1")
    memory.add_short_term("assistant", "Response 1")
    memory.add_short_term("user", "Hello 2")
    assert len(memory.get_short_term(10)) == 3

    # Adding 4th item should evict the oldest
    memory.add_short_term("assistant", "Response 2")
    items = memory.get_short_term(10)
    assert len(items) == 3
    assert items[0].content == "Response 1"
    assert items[-1].content == "Response 2"


def test_short_term_get_subset_and_clear():
    memory = AgentMemory(max_short_term=10)
    for i in range(5):
        memory.add_short_term("system", f"Note {i}", metadata={"idx": i})

    last_two = memory.get_short_term(2)
    assert len(last_two) == 2
    assert last_two[-1].metadata["idx"] == 4

    memory.clear_short_term()
    assert len(memory.get_short_term()) == 0


def test_working_memory_lifecycle():
    memory = AgentMemory()
    memory.set_working("current_subtask", "extract_tables")
    memory.set_working("chunk_offset", 42)

    assert memory.get_working("current_subtask") == "extract_tables"
    assert memory.get_working("chunk_offset") == 42
    assert memory.get_working("nonexistent", default="fallback") == "fallback"

    memory.clear_working()
    assert memory.get_working("current_subtask") is None


def test_long_term_memory():
    memory = AgentMemory()
    memory.set_long_term("summary", "Document describes quantum computing.")
    memory.set_long_term("metrics", {"accuracy": 0.98})

    assert memory.get_long_term("summary") == "Document describes quantum computing."
    assert "metrics" in memory.list_long_term_keys()
    assert memory.get_long_term("missing", "default_val") == "default_val"
