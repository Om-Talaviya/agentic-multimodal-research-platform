"""Agent state model and explicit state transition validation."""

from enum import Enum
from typing import Dict, Set


class AgentState(str, Enum):
    """Lifecycle states of an agent execution."""

    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_TOOL = "waiting_for_tool"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class InvalidStateTransitionError(Exception):
    """Raised when an illegal agent state transition is attempted."""

    def __init__(self, from_state: AgentState, to_state: AgentState) -> None:
        super().__init__(f"Invalid agent state transition from '{from_state.value}' to '{to_state.value}'")
        self.from_state = from_state
        self.to_state = to_state


# Explicit set of valid state transitions
VALID_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.CREATED: {
        AgentState.QUEUED,
        AgentState.RUNNING,
        AgentState.CANCELLED,
    },
    AgentState.QUEUED: {
        AgentState.RUNNING,
        AgentState.CANCELLED,
    },
    AgentState.RUNNING: {
        AgentState.WAITING_FOR_TOOL,
        AgentState.WAITING_FOR_APPROVAL,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
        AgentState.TIMED_OUT,
    },
    AgentState.WAITING_FOR_TOOL: {
        AgentState.RUNNING,
        AgentState.FAILED,
        AgentState.CANCELLED,
        AgentState.TIMED_OUT,
    },
    AgentState.WAITING_FOR_APPROVAL: {
        AgentState.RUNNING,
        AgentState.CANCELLED,
        AgentState.FAILED,
        AgentState.TIMED_OUT,
    },
    # Terminal states have no valid subsequent transitions
    AgentState.COMPLETED: set(),
    AgentState.FAILED: set(),
    AgentState.CANCELLED: set(),
    AgentState.TIMED_OUT: set(),
}

TERMINAL_STATES: Set[AgentState] = {
    AgentState.COMPLETED,
    AgentState.FAILED,
    AgentState.CANCELLED,
    AgentState.TIMED_OUT,
}


class AgentStateMachine:
    """Manages and validates agent state transitions."""

    def __init__(self, initial_state: AgentState = AgentState.CREATED) -> None:
        self._state = initial_state

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def is_terminal(self) -> bool:
        return self._state in TERMINAL_STATES

    def transition_to(self, new_state: AgentState) -> None:
        """Validate and execute transition to new state."""
        allowed = VALID_TRANSITIONS.get(self._state, set())
        if new_state not in allowed:
            raise InvalidStateTransitionError(self._state, new_state)
        self._state = new_state
