"""Web fetch tool definition."""

from html.parser import HTMLParser
import asyncio
import httpx
import ipaddress
import socket
from urllib.parse import urlparse
from tools.base import Permission, Tool, ToolParameter, ToolSchema
from shared.logging import get_logger

logger = get_logger(__name__)


def _is_ip_allowed(ip_str: str) -> bool:
    """Check if an IP address is allowed for outbound requests.

    Blocks: loopback, private, link-local, reserved, and unspecified addresses.
    Allows: public IPv4 and IPv6 addresses.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False

    if ip.is_loopback:
        return False
    if ip.is_private:
        return False
    if ip.is_link_local:
        return False
    if ip.is_reserved:
        return False
    if ip.is_unspecified:
        return False
    if ip.is_multicast:
        return False

    return True


async def _resolve_and_validate_hostname(hostname: str) -> None:
    """Resolve hostname and validate all resolved IPs are public.

    Raises:
        ValueError: If any resolved IP is not allowed (private, loopback, etc.)
        socket.gaierror: If hostname cannot be resolved
    """
    clean_host = hostname.strip("[]")
    try:
        ipaddress.ip_address(clean_host)
        if not _is_ip_allowed(clean_host):
            raise ValueError(f"Blocked IP address: {clean_host}")
        return
    except ValueError as e:
        if "Blocked IP address" in str(e):
            raise
        # Not an IP literal, proceed to DNS resolution

    try:
        infos = socket.getaddrinfo(
            clean_host, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )
    except socket.gaierror as e:
        raise ValueError(f"Failed to resolve hostname: {e}")

    for info in infos:
        ip = info[4][0]
        if not _is_ip_allowed(ip):
            raise ValueError(f"Blocked IP address: {ip}")


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
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return "Error fetching URL: Only HTTP and HTTPS schemes are allowed"

            hostname = parsed.hostname
            if not hostname:
                return "Error fetching URL: Invalid URL - no hostname"

            await _resolve_and_validate_hostname(hostname)

            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0, follow_redirects=True)
                response.raise_for_status()

                parser = TextExtractor()
                parser.feed(response.text)
                content = " ".join(parser.text)

                if len(content) > max_length:
                    content = content[:max_length] + "... [truncated]"

                return content
        except ValueError as e:
            logger.warning("Web fetch blocked by SSRF protection", url=url, error=str(e))
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            logger.error("Web fetch failed", url=url, error=str(e))
            return f"Error fetching URL: {str(e)}"
