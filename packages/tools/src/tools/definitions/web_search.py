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


from tools.definitions.web_fetch import WebFetchTool

__all__ = ["WebSearchTool", "WebFetchTool"]