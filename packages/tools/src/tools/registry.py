"""Tool registry for discovery and execution."""

from typing import Any
from tools.base import Tool, ToolSchema


class ToolRegistry:
    """Registry for tool discovery and execution."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool instance."""
        self._tools[tool.schema.name] = tool
    
    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all(self) -> list[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_schemas(self) -> list[dict]:
        """Get all tool schemas in OpenAI format."""
        return [tool.to_openai_format() for tool in self._tools.values()]
    
    def get_names(self) -> list[str]:
        """Get all tool names."""
        return list(self._tools.keys())
    
    async def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return await tool.execute(**kwargs)
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all tools."""
        self._tools.clear()


# Global registry instance
tool_registry = ToolRegistry()