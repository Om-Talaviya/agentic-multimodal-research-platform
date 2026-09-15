# AI Research OS - Official Python SDK

`ai-research-os` is the official Python async developer SDK for interacting with the **Agentic Multimodal Research Platform** (AI Research OS).

## Installation

```bash
pip install ai-research-os
```

## Quickstart

```python
import asyncio
from ai_research_os import AIResearchClient

async def main():
    client = AIResearchClient(
        api_key="os_live_your_api_key_here",
        base_url="http://localhost:8000"
    )

    # 1. Launch a deep research investigation
    job = await client.research.create(
        question="What are the latest breakthroughs in CRISPR epigenetic silencing for hepatic disorders?",
        domain="genomics",
        scope="deep"
    )
    print(f"Launched Job: {job.job_id}")

    # 2. Poll until autonomous agents finish synthesis
    finished_job = await client.research.poll_until_complete(job.job_id)
    print("Confidence:", finished_job.report.confidence_score)
    print("Summary:", finished_job.report.executive_summary)

    # 3. Check token consumption and rate limits
    usage = await client.usage.get_summary()
    print("Tokens consumed:", usage.total_tokens_consumed)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features
- Full async support with `httpx` connection pooling
- Type annotations & Pydantic v2 data models
- Automatic token quota & rate limit error handling
- Polling helpers with configurable timeout and backoff
