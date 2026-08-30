"""Prometheus metrics exposition route."""

from fastapi import APIRouter, Response
from api.middleware.metrics import metrics_collector

router = APIRouter(tags=["monitoring"])


@router.get("/metrics")
async def get_metrics() -> Response:
    """Expose Prometheus formatted application metrics."""
    metrics_text = metrics_collector.generate_prometheus_text()
    return Response(
        content=metrics_text,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
