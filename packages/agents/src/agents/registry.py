"""Agent registry for discovery and instantiation."""

from typing import Type
from agents.base import Agent


class AgentRegistry:
    """Registry for agent discovery and instantiation."""
    
    def __init__(self):
        self._agents: dict[str, Type[Agent]] = {}
    
    def register(self, name: str, agent_class: Type[Agent]) -> None:
        self._agents[name] = agent_class
    
    def get(self, name: str) -> Type[Agent] | None:
        return self._agents.get(name)
    
    def create(self, name: str, config: dict | None = None) -> Agent:
        agent_class = self.get(name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {name}")
        return agent_class(config)
    
    def list_agents(self) -> list[dict]:
        return [
            {
                "name": name,
                "description": cls.description,
                "capabilities": list(cls.capabilities),
            }
            for name, cls in self._agents.items()
        ]


# Global registry instance
registry = AgentRegistry()