"""Tests for tools package."""

import pytest
from tools.base import Tool, ToolSchema, ToolParameter, Permission
from tools.registry import ToolRegistry, tool_registry
from tools.definitions.web_search import WebSearchTool, WebFetchTool
from tools.definitions.document_read import DocumentReadTool


class MockTool(Tool):
    """Mock tool for testing."""
    
    schema = ToolSchema(
        name="mock_tool",
        description="A mock tool for testing",
        parameters=[
            ToolParameter(name="input", type="string", description="Input string"),
        ],
        returns="string",
        permissions=[Permission.WEB_ACCESS],
    )
    
    async def execute(self, input: str) -> str:
        return f"Processed: {input}"


def test_tool_schema():
    """Test ToolSchema creation."""
    schema = ToolSchema(
        name="test_tool",
        description="Test tool",
        parameters=[
            ToolParameter(name="param1", type="string", description="Param 1"),
            ToolParameter(name="param2", type="integer", description="Param 2", required=False),
        ],
        returns="string",
    )
    
    assert schema.name == "test_tool"
    assert len(schema.parameters) == 2
    assert schema.parameters[0].required is True
    assert schema.parameters[1].required is False


def test_tool_openai_format():
    """Test tool OpenAI format conversion."""
    tool = MockTool()
    openai_format = tool.to_openai_format()
    
    assert openai_format["type"] == "function"
    assert openai_format["function"]["name"] == "mock_tool"
    assert openai_format["function"]["description"] == "A mock tool for testing"
    assert "input" in openai_format["function"]["parameters"]["properties"]
    assert "input" in openai_format["function"]["parameters"]["required"]


def test_tool_permissions():
    """Test tool permission checking."""
    tool = MockTool()
    
    # Agent has required permission
    assert tool.check_permissions({Permission.WEB_ACCESS, Permission.DOCUMENT_ACCESS}) is True
    
    # Agent lacks required permission
    assert tool.check_permissions({Permission.DOCUMENT_ACCESS}) is False
    
    # No permissions required
    class NoPermTool(Tool):
        schema = ToolSchema(name="no_perm", description="No permissions")
        async def execute(self): pass
    
    no_perm = NoPermTool()
    assert no_perm.check_permissions(set()) is True


def test_tool_registry():
    """Test ToolRegistry."""
    registry = ToolRegistry()
    
    # Register tool
    tool = MockTool()
    registry.register(tool)
    
    # Get tool
    fetched = registry.get("mock_tool")
    assert fetched is tool
    
    # Get all
    all_tools = registry.get_all()
    assert len(all_tools) == 1
    
    # Get schemas
    schemas = registry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "mock_tool"
    
    # Execute tool
    import asyncio
    result = asyncio.run(registry.execute("mock_tool", input="test"))
    assert result == "Processed: test"
    
    # Execute unknown tool
    with pytest.raises(ValueError):
        asyncio.run(registry.execute("unknown_tool"))


def test_global_tool_registry():
    """Test global tool registry."""
    # Clear any existing
    tool_registry.clear()
    
    # Register built-in tools
    tool_registry.register(WebSearchTool())
    tool_registry.register(WebFetchTool())
    tool_registry.register(DocumentReadTool())
    
    tools = tool_registry.get_all()
    assert len(tools) == 3
    names = {t.schema.name for t in tools}
    assert names == {"web_search", "web_fetch", "document_read"}
    
    schemas = tool_registry.get_schemas()
    assert len(schemas) == 3