"""Prometheus metrics collector and tracking middleware."""

from collections import defaultdict
import time
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class MetricsCollector:
    """In-memory Prometheus metrics registry and accumulator."""

    def __init__(self) -> None:
        self.request_counts: Dict[Tuple[str, str, int], int] = defaultdict(int)
        self.request_durations: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        self.error_counts: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self.model_calls: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self.model_tokens: Dict[Tuple[str, str], int] = defaultdict(int)
        self.agent_runs: Dict[Tuple[str, str], int] = defaultdict(int)
        self.active_requests: int = 0

    def record_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        """Record HTTP request duration and status."""
        normalized_path = self._normalize_path(path)
        self.request_counts[(method, normalized_path, status_code)] += 1
        self.request_durations[(method, normalized_path)].append(duration)
        if len(self.request_durations[(method, normalized_path)]) > 5000:
            # Keep bounded history
            self.request_durations[(method, normalized_path)] = self.request_durations[(method, normalized_path)][-2500:]

        if status_code >= 400:
            self.error_counts[(method, normalized_path, str(status_code))] += 1

    def record_model_call(self, provider: str, model: str, success: bool, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        """Record LLM/Vision model invocation."""
        status_str = "success" if success else "error"
        self.model_calls[(provider, model, status_str)] += 1
        if prompt_tokens > 0:
            self.model_tokens[(model, "prompt")] += prompt_tokens
        if completion_tokens > 0:
            self.model_tokens[(model, "completion")] += completion_tokens

    def record_agent_run(self, agent_name: str, success: bool) -> None:
        """Record Agent execution."""
        status_str = "success" if success else "failed"
        self.agent_runs[(agent_name, status_str)] += 1

    def _normalize_path(self, path: str) -> str:
        """Normalize UUIDs and IDs in path for clean Prometheus labels."""
        import re
        # Replace UUIDs
        p = re.sub(r"[0-9a-fA-F-]{36}", ":id", path)
        # Replace integer IDs
        p = re.sub(r"/\d+/", "/:id/", p)
        return p

    def generate_prometheus_text(self) -> str:
        """Render all metrics in Prometheus text exposition format."""
        lines: List[str] = []

        # 1. http_requests_total
        lines.append("# HELP http_requests_total Total number of HTTP requests processed.")
        lines.append("# TYPE http_requests_total counter")
        for (method, path, status), count in sorted(self.request_counts.items()):
            lines.append(f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}')

        # 2. http_request_duration_seconds summary
        lines.append("# HELP http_request_duration_seconds Latency of HTTP requests in seconds.")
        lines.append("# TYPE http_request_duration_seconds summary")
        for (method, path), durations in sorted(self.request_durations.items()):
            if durations:
                total_sum = sum(durations)
                total_count = len(durations)
                lines.append(f'http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {total_sum:.6f}')
                lines.append(f'http_request_duration_seconds_count{{method="{method}",path="{path}"}} {total_count}')

        # 3. http_errors_total
        lines.append("# HELP http_errors_total Total number of HTTP errors (>=400).")
        lines.append("# TYPE http_errors_total counter")
        for (method, path, status), count in sorted(self.error_counts.items()):
            lines.append(f'http_errors_total{{method="{method}",path="{path}",status="{status}"}} {count}')

        # 4. model_calls_total
        lines.append("# HELP model_calls_total Total AI model provider invocations.")
        lines.append("# TYPE model_calls_total counter")
        for (provider, model, status), count in sorted(self.model_calls.items()):
            lines.append(f'model_calls_total{{provider="{provider}",model="{model}",status="{status}"}} {count}')

        # 5. model_tokens_total
        lines.append("# HELP model_tokens_total Total tokens processed by AI models.")
        lines.append("# TYPE model_tokens_total counter")
        for (model, token_type), count in sorted(self.model_tokens.items()):
            lines.append(f'model_tokens_total{{model="{model}",type="{token_type}"}} {count}')

        # 6. agent_runs_total
        lines.append("# HELP agent_runs_total Total agent run executions.")
        lines.append("# TYPE agent_runs_total counter")
        for (agent_name, status), count in sorted(self.agent_runs.items()):
            lines.append(f'agent_runs_total{{agent="{agent_name}",status="{status}"}} {count}')

        # 7. active_requests
        lines.append("# HELP active_requests Number of currently in-flight requests.")
        lines.append("# TYPE active_requests gauge")
        lines.append(f"active_requests {max(0, self.active_requests)}")

        return "\n".join(lines) + "\n"


metrics_collector = MetricsCollector()


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware capturing request count and latency for Prometheus."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Don't track metrics endpoint itself to avoid recursion
        if request.url.path in ("/metrics", "/api/v1/metrics"):
            return await call_next(request)

        metrics_collector.active_requests += 1
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            metrics_collector.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )
            return response
        except Exception:
            duration = time.perf_counter() - start_time
            metrics_collector.record_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=duration,
            )
            raise
        finally:
            metrics_collector.active_requests = max(0, metrics_collector.active_requests - 1)
