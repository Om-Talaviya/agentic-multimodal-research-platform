"""Main async client for AI Research OS."""

import asyncio
from typing import Any, Dict, List, Optional
import httpx

from .exceptions import (
    AIResearchOSError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
    APIError,
)
from .models import (
    ResearchJobResponse,
    DocumentIngestResponse,
    ApiUsageSummary,
)


class ResearchService:
    """Namespace for executing and monitoring autonomous research jobs."""

    def __init__(self, client: "AIResearchClient") -> None:
        self._client = client

    async def create(
        self,
        question: str,
        objective: Optional[str] = None,
        domain: str = "general",
        scope: str = "deep",
        project_id: Optional[str] = None,
        timeout_seconds: int = 600,
    ) -> ResearchJobResponse:
        """Launch an autonomous multi-agent research investigation."""
        payload = {
            "question": question,
            "objective": objective,
            "domain": domain,
            "scope": scope,
            "project_id": project_id,
            "timeout_seconds": timeout_seconds,
        }
        res = await self._client._request("POST", "/api/v1/developer/research", json=payload)
        return ResearchJobResponse(**res)

    async def get(self, job_id: str) -> ResearchJobResponse:
        """Fetch the full telemetry, task graph, and report of a research job."""
        res = await self._client._request("GET", f"/api/v1/developer/research/{job_id}")
        return ResearchJobResponse(**res)

    async def list(self, limit: int = 50, offset: int = 0) -> List[ResearchJobResponse]:
        """List recent programmatic research jobs."""
        res = await self._client._request(
            "GET", "/api/v1/developer/research", params={"limit": limit, "offset": offset}
        )
        return [ResearchJobResponse(**item) for item in res.get("jobs", [])]

    async def poll_until_complete(
        self,
        job_id: str,
        interval_seconds: float = 2.0,
        max_wait_seconds: float = 300.0,
    ) -> ResearchJobResponse:
        """Poll the research job until it reaches 'completed' or 'failed' status."""
        elapsed = 0.0
        while elapsed < max_wait_seconds:
            job = await self.get(job_id)
            if job.status in ("completed", "failed", "cancelled"):
                return job
            await asyncio.sleep(interval_seconds)
            elapsed += interval_seconds
        raise TimeoutError(f"Research job {job_id} did not complete within {max_wait_seconds}s.")


class DocumentService:
    """Namespace for ingesting multimodal documents and text corpora."""

    def __init__(self, client: "AIResearchClient") -> None:
        self._client = client

    async def ingest_text(
        self,
        title: str,
        text_content: str,
        filename: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> DocumentIngestResponse:
        """Ingest raw scientific text into vector knowledge store."""
        payload = {
            "title": title,
            "text_content": text_content,
            "filename": filename,
            "project_id": project_id,
        }
        res = await self._client._request("POST", "/api/v1/developer/documents", json=payload)
        return DocumentIngestResponse(**res)


class UsageService:
    """Namespace for checking developer API token consumption and quotas."""

    def __init__(self, client: "AIResearchClient") -> None:
        self._client = client

    async def get_summary(self) -> ApiUsageSummary:
        """Retrieve rate limits, remaining tokens, and usage metrics."""
        res = await self._client._request("GET", "/api/v1/developer/usage")
        return ApiUsageSummary(**res)


class AIResearchClient:
    """Primary asynchronous developer client for the AI Research OS."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

        # Service namespaces
        self.research = ResearchService(self)
        self.documents = DocumentService(self)
        self.usage = UsageService(self)

    async def __aenter__(self) -> "AIResearchClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "X-API-Key": self.api_key,
                    "User-Agent": "AIResearchOS-PythonSDK/1.1.0",
                    "Accept": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        client = await self._ensure_client()
        try:
            response = await client.request(method, path, params=params, json=json)
        except httpx.RequestError as exc:
            raise AIResearchOSError(f"Network error communicating with {self.base_url}: {exc}") from exc

        if response.status_code in (200, 201, 202):
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError("Invalid or expired API key.")
        elif response.status_code == 403:
            raise AuthenticationError("Insufficient permissions or inactive API key.")
        elif response.status_code == 404:
            raise ResourceNotFoundError(f"Endpoint or resource not found: {path}")
        elif response.status_code == 422:
            raise ValidationError(f"Schema validation error: {response.text}")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded for developer key.")
        else:
            raise APIError(
                status_code=response.status_code,
                detail=response.text,
                payload=response.json() if response.headers.get("content-type") == "application/json" else {},
            )

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
