"""Concurrent load test benchmark for Research Platform API endpoints."""

import asyncio
import statistics
import time
from typing import Dict, List, Optional
import httpx


async def run_single_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    json_data: Optional[dict] = None,
) -> tuple[bool, float, int]:
    """Execute a single HTTP request and measure latency."""
    start = time.perf_counter()
    try:
        if method.upper() == "POST":
            resp = await client.post(endpoint, json=json_data)
        else:
            resp = await client.get(endpoint)
        latency = time.perf_counter() - start
        return (resp.status_code < 400, latency, resp.status_code)
    except Exception:
        latency = time.perf_counter() - start
        return (False, latency, 500)


async def run_load_benchmark(
    base_url: str = "http://localhost:8000",
    endpoint: str = "/api/v1/health",
    total_requests: int = 50,
    concurrency: int = 10,
    in_process_app: Optional[object] = None,
) -> Dict[str, float]:
    """Run concurrent load test against API endpoint and calculate latency statistics."""
    latencies: List[float] = []
    success_count = 0
    failure_count = 0

    semaphore = asyncio.Semaphore(concurrency)

    async def worker(client: httpx.AsyncClient):
        nonlocal success_count, failure_count
        async with semaphore:
            success, latency, _ = await run_single_request(client, "GET", endpoint)
            latencies.append(latency)
            if success:
                success_count += 1
            else:
                failure_count += 1

    start_total = time.perf_counter()
    if in_process_app:
        transport = httpx.ASGITransport(app=in_process_app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            tasks = [worker(client) for _ in range(total_requests)]
            await asyncio.gather(*tasks)
    else:
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
            tasks = [worker(client) for _ in range(total_requests)]
            await asyncio.gather(*tasks)

    total_duration = time.perf_counter() - start_total

    sorted_latencies = sorted(latencies) if latencies else [0.0]
    p95_idx = int(len(sorted_latencies) * 0.95)
    p99_idx = int(len(sorted_latencies) * 0.99)

    stats = {
        "total_requests": float(total_requests),
        "success_count": float(success_count),
        "failure_count": float(failure_count),
        "total_duration_seconds": total_duration,
        "throughput_rps": float(total_requests / total_duration) if total_duration > 0 else 0.0,
        "avg_latency_ms": statistics.mean(sorted_latencies) * 1000,
        "median_latency_ms": statistics.median(sorted_latencies) * 1000,
        "p95_latency_ms": sorted_latencies[min(p95_idx, len(sorted_latencies) - 1)] * 1000,
        "p99_latency_ms": sorted_latencies[min(p99_idx, len(sorted_latencies) - 1)] * 1000,
        "max_latency_ms": max(sorted_latencies) * 1000,
    }

    print("\n--- Load Test Benchmark Results ---")
    print(f"Total Requests:    {stats['total_requests']}")
    print(f"Successful:        {stats['success_count']}")
    print(f"Failed:            {stats['failure_count']}")
    print(f"Throughput:        {stats['throughput_rps']:.2f} req/s")
    print(f"Avg Latency:       {stats['avg_latency_ms']:.2f} ms")
    print(f"P95 Latency:       {stats['p95_latency_ms']:.2f} ms")
    print(f"P99 Latency:       {stats['p99_latency_ms']:.2f} ms")
    print("-----------------------------------\n")

    return stats


if __name__ == "__main__":
    import sys
    from pathlib import Path
    root_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root_dir / "apps" / "api" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "ai" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "shared" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "database" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "tools" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "agents" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "research" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "ingestion" / "src"))
    sys.path.insert(0, str(root_dir / "packages" / "retrieval" / "src"))

    from main import app
    asyncio.run(run_load_benchmark(in_process_app=app, total_requests=50, concurrency=10))
