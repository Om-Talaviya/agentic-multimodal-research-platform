"""Web fetch tool definition."""

from html.parser import HTMLParser
import httpx
from tools.base import Permission, Tool, ToolParameter, ToolSchema
from shared.logging import get_logger

logger = get_logger(__name__)


class TextExtractor(HTMLParser):
    """Simple HTML to clean text extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.ignore = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in ("script", "style", "noscript", "svg", "head"):
            self.ignore = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("script", "style", "noscript", "svg", "head"):
            self.ignore = False

    def handle_data(self, data: str) -> None:
        if not self.ignore and data.strip():
            self.text.append(data.strip())


class WebFetchTool(Tool):
    """Fetch and extract readable text content from a URL."""

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
        """Fetch URL content and extract clean text."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0, follow_redirects=True)
                response.raise_for_status()

                parser = TextExtractor()
                parser.feed(response.text)
                content = " ".join(parser.text)

                if len(content) > max_length:
                    content = content[:max_length] + "... [truncated]"

                return content
        except Exception as e:
            logger.error("Web fetch failed", url=url, error=str(e))
            return f"Error fetching URL: {str(e)}"
