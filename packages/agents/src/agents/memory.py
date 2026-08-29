"""Agent memory framework with bounded short-term, working, and long-term storage."""

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryItem:
    """An individual memory entry."""

    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMemory:
    """Multi-tiered agent memory for execution context and knowledge persistence.

    - short_term: Bounded deque of recent interactions / reasoning steps.
    - working: Key-value scratchpad for current task step state.
    - long_term: Key-value knowledge store for verified facts, summaries, and claims.
    """

    max_short_term: int = 20
    _short_term: deque[MemoryItem] = field(default_factory=deque)
    long_term: Dict[str, Any] = field(default_factory=dict)
    working: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self._short_term, deque) or self._short_term.maxlen != self.max_short_term:
            self._short_term = deque(self._short_term, maxlen=self.max_short_term)

    # --- Short-term memory methods ---
    def add_short_term(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an interaction to bounded short-term memory."""
        item = MemoryItem(role=role, content=content, metadata=metadata or {})
        self._short_term.append(item)

    def get_short_term(self, n: int = 10) -> List[MemoryItem]:
        """Get the n most recent items from short-term memory."""
        items = list(self._short_term)
        return items[-n:] if n < len(items) else items

    def clear_short_term(self) -> None:
        """Clear all short-term memories."""
        self._short_term.clear()

    # --- Working memory methods ---
    def set_working(self, key: str, value: Any) -> None:
        """Set a variable in task working memory."""
        self.working[key] = value

    def get_working(self, key: str, default: Any = None) -> Any:
        """Retrieve a variable from task working memory."""
        return self.working.get(key, default)

    def clear_working(self) -> None:
        """Clear working scratchpad state."""
        self.working.clear()

    # --- Long-term memory methods ---
    def set_long_term(self, key: str, value: Any) -> None:
        """Persist a fact or finding in long-term memory."""
        self.long_term[key] = value

    def get_long_term(self, key: str, default: Any = None) -> Any:
        """Retrieve a fact or finding from long-term memory."""
        return self.long_term.get(key, default)

    def list_long_term_keys(self) -> List[str]:
        """List all stored long-term keys."""
        return list(self.long_term.keys())
