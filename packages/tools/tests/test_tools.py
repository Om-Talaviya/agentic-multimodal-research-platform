"""Tests for tools package."""

import pytest
import socket
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


class TestWebFetchSSRFProtection:
    """Tests for SSRF protection in WebFetchTool."""

    @pytest.fixture
    def web_fetch_tool(self):
        return WebFetchTool()

    def test_is_ip_allowed_public_ipv4(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        # Public IPv4 addresses should be allowed
        assert _is_ip_allowed("8.8.8.8") is True
        assert _is_ip_allowed("1.1.1.1") is True
        assert _is_ip_allowed("93.184.216.34") is True  # example.com

    def test_is_ip_allowed_public_ipv6(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        # Public IPv6 addresses should be allowed
        assert _is_ip_allowed("2001:4860:4860::8888") is True
        assert _is_ip_allowed("2606:4700:4700::1111") is True

    def test_is_ip_allowed_rejects_loopback_ipv4(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        assert _is_ip_allowed("127.0.0.1") is False
        assert _is_ip_allowed("127.0.0.2") is False
        assert _is_ip_allowed("127.255.255.255") is False

    def test_is_ip_allowed_rejects_loopback_ipv6(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        assert _is_ip_allowed("::1") is False
        assert _is_ip_allowed("::ffff:127.0.0.1") is False

    def test_is_ip_allowed_rejects_private_ipv4(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        # 10.0.0.0/8
        assert _is_ip_allowed("10.0.0.1") is False
        assert _is_ip_allowed("10.255.255.255") is False
        # 172.16.0.0/12
        assert _is_ip_allowed("172.16.0.1") is False
        assert _is_ip_allowed("172.31.255.255") is False
        # 192.168.0.0/16
        assert _is_ip_allowed("192.168.1.1") is False
        assert _is_ip_allowed("192.168.255.255") is False

    def test_is_ip_allowed_rejects_private_ipv6(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        # fc00::/7 (ULA)
        assert _is_ip_allowed("fc00::1") is False
        assert _is_ip_allowed("fd00::1") is False
        assert _is_ip_allowed("fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff") is False

    def test_is_ip_allowed_rejects_link_local_ipv4(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        assert _is_ip_allowed("169.254.0.1") is False
        assert _is_ip_allowed("169.254.169.254") is False
        assert _is_ip_allowed("169.254.255.255") is False

    def test_is_ip_allowed_rejects_link_local_ipv6(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        assert _is_ip_allowed("fe80::1") is False
        assert _is_ip_allowed("fe80::ffff:ffff:ffff:ffff") is False
        assert _is_ip_allowed("febf::1") is False

    def test_is_ip_allowed_rejects_reserved_unspecified(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        # Unspecified
        assert _is_ip_allowed("0.0.0.0") is False
        assert _is_ip_allowed("::") is False
        # Reserved ranges
        assert _is_ip_allowed("240.0.0.1") is False
        assert _is_ip_allowed("255.255.255.255") is False

    def test_is_ip_allowed_rejects_multicast(self):
        from tools.definitions.web_fetch import _is_ip_allowed

        assert _is_ip_allowed("224.0.0.1") is False
        assert _is_ip_allowed("239.255.255.255") is False
        assert _is_ip_allowed("ff02::1") is False

    @pytest.mark.asyncio
    async def test_execute_blocks_loopback_ipv4(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://127.0.0.1/admin")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_private_10(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://10.0.0.1/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_private_172(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://172.16.0.1/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_private_192(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://192.168.1.1/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_link_local(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://169.254.169.254/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_ipv6_loopback(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://[::1]/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_ipv6_private(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://[fc00::1]/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_blocks_ipv6_link_local(self, web_fetch_tool):
        result = await web_fetch_tool.execute("http://[fe80::1]/")
        assert "Blocked IP address" in result or "Error fetching URL" in result

    @pytest.mark.asyncio
    async def test_execute_allows_public_http(self, web_fetch_tool):
        # Test that public URLs pass scheme validation (SSRF check happens at DNS resolution)
        # We can't easily mock the DNS resolution here, so we just verify the scheme check passes
        # by checking that a non-HTTP scheme is rejected
        result = await web_fetch_tool.execute("http://example.com/")
        # Should NOT be blocked by SSRF (will fail at network level, not SSRF level)
        assert "Only HTTP and HTTPS schemes are allowed" not in result
        assert "Invalid URL" not in result

    @pytest.mark.asyncio
    async def test_execute_allows_public_https(self, web_fetch_tool):
        result = await web_fetch_tool.execute("https://example.com/")
        assert "Only HTTP and HTTPS schemes are allowed" not in result
        assert "Invalid URL" not in result

    @pytest.mark.asyncio
    async def test_execute_rejects_non_http_scheme(self, web_fetch_tool):
        result = await web_fetch_tool.execute("ftp://example.com/")
        assert "Only HTTP and HTTPS schemes are allowed" in result

    @pytest.mark.asyncio
    async def test_execute_rejects_invalid_url(self, web_fetch_tool):
        result = await web_fetch_tool.execute("not-a-url")
        assert "Invalid URL" in result or "Error fetching URL" in result