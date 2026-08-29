"""Web search tool definition."""

import httpx
from tools.base import Tool, ToolSchema, ToolParameter, Permission
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


class WebSearchTool(Tool):
    """Search the web using a search API."""
    
    schema = ToolSchema(
        name="web_search",
        description="Search the web for information. Returns a list of results with title, URL, and snippet.",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum number of results to return",
                required=False,
                default=10,
            ),
        ],
        returns="List of search results with title, url, snippet",
        permissions=[Permission.WEB_ACCESS],
    )
    
    async def execute(self, query: str, max_results: int = 10) -> list[dict]:
        if not settings.search_api_url or not settings.search_api_key:
            logger.warning("Search API not configured, returning empty results")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.search_api_url}/search",
                    json={"query": query, "max_results": max_results},
                    headers={"Authorization": f"Bearer {settings.search_api_key}"},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.error("Web search failed", error=str(e))
            return []


class WebFetchTool(Tool):
    """Fetch and extract content from a URL."""
    
    schema = ToolSchema(
        name="web_fetch",
        description="Fetch and extract readable content from a URL",
        parameters=[
            ToolParameter(
                name="url",
                type="string",
                description="URL to fetch",
                required=True,
            ),
            ToolParameter(
                name="max_length",
                type="integer",
                description="Maximum content length to return",
                required=False,
                default=50000,
            ),
        ],
        returns="Extracted text content",
        permissions=[Permission.WEB_ACCESS],
    )
    
    async def execute(self, url: str, max_length: int = 50000) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0, follow_redirects=True)
                response.raise_for_status()
                
                # Simple HTML extraction (for production, use readability-lxml or similar)
                from html.parser import HTMLParser
                
                class TextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.text = []
                        self.ignore = False
                    
                    def handle_starttag(self, tag, attrs):
                        if tag in ('script', 'style', 'noscript'):
                            self.ignore = True
                    
                    def handle_endtag(self, tag):
                        if tag in ('script', 'style', 'noscript'):
                            self.ignore = False
                    
                    def handle_data(self, data):
                        if not self.ignore and data.strip():
                            self.text.append(data.strip())
                
                parser = TextExtractor()
                parser.feed(response.text)
                content = ' '.join(parser.text)
                
                # Truncate if needed
                if len(content) > max_length:
                    content = content[:max_length] + "... [truncated]"
                
                return content
        except Exception as e:
            logger.error("Web fetch failed", url=url, error=str(e))
            return f"Error fetching URL: {str(e)}"