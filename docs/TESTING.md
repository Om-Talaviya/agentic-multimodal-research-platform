# Testing Strategy

## Overview

Multi-layered testing approach ensuring reliability without expensive external API calls.

## Test Pyramid

```
           ┌─────────────┐
           │   E2E Tests │  ← Few, critical paths
           ├─────────────┤
       ┌───│Integration  │───┐
       │   │   Tests     │   │
       │   ├─────────────┤   │
       │   │   Unit      │   │
       │   │   Tests     │   │
       │   └─────────────┘   │
       └─────────────────────┘
```

## Unit Tests

### Target: >80% coverage for core packages

```bash
# Run unit tests
cd apps/api && pytest tests/unit -v --cov=src --cov-report=term-missing
cd apps/web && npm run test:unit
```

### Key Areas

```python
# tests/unit/ai/test_router.py
import pytest
from packages.ai.providers.router import ModelRouter
from packages.ai.providers.llm import LLMProvider
from packages.ai.schemas import ModelCapabilities, ModelCapability

class MockProvider(LLMProvider):
    def __init__(self, name, capabilities, is_local=False):
        self._name = name
        self._capabilities = capabilities
        self._is_local = is_local
    
    @property
    def name(self): return self._name
    @property def capabilities(self): return self._capabilities
    @property def is_local(self): return self._is_local
    async def complete(self, request): ...
    async def health_check(self): return True

def test_router_selects_local_first():
    router = ModelRouter(
        llm_providers=[
            MockProvider("cloud", {ModelCapability.REASONING}, is_local=False),
            MockProvider("local", {ModelCapability.REASONING}, is_local=True),
        ],
        vision_providers=[],
        embedding_providers=[],
        reranker_providers=[],
    )
    
    provider = router.select_llm(ModelCapabilities({ModelCapability.REASONING}))
    assert provider.name == "local"

def test_router_raises_on_no_match():
    router = ModelRouter(
        llm_providers=[MockProvider("cloud", {ModelCapability.CODING})],
        vision_providers=[],
        embedding_providers=[],
        reranker_providers=[],
    )
    
    with pytest.raises(NoSuitableModelError):
        router.select_llm(ModelCapabilities({ModelCapability.REASONING}))
```

```python
# tests/unit/ingestion/test_chunking.py
from packages.ingestion.chunking import FixedSizeChunker, SemanticChunker
from packages.ingestion.parsers.base import ParsedDocument

def test_fixed_size_chunker():
    doc = ParsedDocument(content="A" * 2500, metadata={})
    chunker = FixedSizeChunker(chunk_size=1000, overlap=200)
    chunks = chunker.chunk(doc)
    
    assert len(chunks) == 3  # 2500 / (1000-200) ≈ 3
    assert chunks[0].content == "A" * 1000
    assert chunks[1].content == "A" * 1000  # overlap handled
    assert chunks[0].end_char == 1000
    assert chunks[1].start_char == 800
```

## Integration Tests

### Target: Database, API, providers

```python
# tests/integration/test_database.py
import pytest
from packages.database.connection import get_session, init_db
from packages.database.repositories import ResearchJobRepository
from packages.database.models.research_job import ResearchJob

@pytest.fixture
async def db_session():
    await init_db()
    async with get_session() as session:
        yield session

async def test_create_and_get_job(db_session):
    repo = ResearchJobRepository(db_session)
    job = ResearchJob(
        request_id=uuid.uuid4(),
        question="Test question",
        objective="Test objective",
    )
    created = await repo.create(job)
    
    fetched = await repo.get(created.id)
    assert fetched is not None
    assert fetched.question == "Test question"
```

```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from apps.api.src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

async def test_create_research_job(client):
    response = await client.post("/api/v1/research", json={
        "question": "What is quantum computing?",
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["question"] == "What is quantum computing?"
    assert data["status"] == "pending"
```

## Agent Tests (with Mocks)

```python
# tests/unit/agents/test_planner_agent.py
import pytest
from packages.agents.planner.planner_agent import PlannerAgent
from packages.agents.base import AgentContext
from packages.research.models import ResearchTask
from packages.ai.providers.router import ModelRouter
from tests.unit.ai.test_mock_provider import MockLLMProvider

@pytest.fixture
def mock_router():
    provider = MockLLMProvider({
        "Research request: Test": '{"objective": "Test", "steps": [], "expected_outputs": []}'
    })
    router = ModelRouter(
        llm_providers=[provider],
        vision_providers=[],
        embedding_providers=[],
        reranker_providers=[],
    )
    return router

@pytest.fixture
def agent_context(mock_router):
    return AgentContext(
        research_job_id="job-1",
        task_id="task-1",
        request_id="req-1",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

async def test_planner_agent_creates_plan(mock_router, agent_context):
    agent = PlannerAgent()
    task = ResearchTask(
        id="task-1",
        job_id="job-1",
        type="planning",
        objective="Test research",
        agent="planner",
    )
    
    result = await agent.run(task, agent_context)
    
    assert result.success
    assert result.output is not None
    assert len(mock_router.llm_providers[0].calls) == 1
```

## Multimodal Tests

```python
# tests/unit/ingestion/test_parsers.py
import pytest
from packages.ingestion.parsers.text import TextParser
from packages.ingestion.parsers.pdf import PDFParser
from packages.ingestion.detection import DocumentFormat, detect_format
from pathlib import Path
import io

def test_detect_format():
    assert detect_format(Path("test.txt")) == DocumentFormat.TEXT
    assert detect_format(Path("test.pdf")) == DocumentFormat.PDF
    assert detect_format(Path("test.docx")) == DocumentFormat.DOCX
    assert detect_format(Path("test.png")) == DocumentFormat.IMAGE

async def test_text_parser():
    parser = TextParser()
    content = b"Hello world\nThis is a test"
    file = io.BytesIO(content)
    
    result = await parser.parse(file, "test.txt")
    
    assert result.content == "Hello world\nThis is a test"
    assert result.metadata["format"] == "text"

async def test_pdf_parser(sample_pdf):
    parser = PDFParser()
    with open(sample_pdf, "rb") as f:
        result = await parser.parse(f, "test.pdf")
    
    assert len(result.content) > 0
    assert result.metadata["page_count"] > 0
```

## Research Pipeline Tests

```python
# tests/integration/test_research_pipeline.py
import pytest
from packages.research.pipeline import ResearchPipeline
from packages.research.models import ResearchRequest

@pytest.fixture
def mock_pipeline():
    # Pipeline with all mocked dependencies
    return ResearchPipeline(
        analyzer=MockAnalyzer(),
        planner=MockPlanner(),
        executor=MockExecutor(),
        verifier=MockVerifier(),
        synthesizer=MockSynthesizer(),
        reporter=MockReporter(),
    )

async def test_full_pipeline(mock_pipeline):
    request = ResearchRequest(question="Test question")
    
    report = await mock_pipeline.run(request)
    
    assert report is not None
    assert report.title is not None
    assert len(report.findings) > 0
```

## AI Evaluation Tests

```python
# tests/eval/test_grounding.py
import pytest
from packages.research.evaluation import evaluate_grounding, evaluate_citations

def test_grounding_score():
    """Test that findings are grounded in evidence."""
    findings = [
        {"claim": "A causes B", "evidence_ids": ["e1", "e2"]},
        {"claim": "C causes D", "evidence_ids": []},  # Ungrounded!
    ]
    evidence = {
        "e1": {"claim": "A causes B", "source": "Study 1"},
        "e2": {"claim": "A correlates with B", "source": "Study 2"},
    }
    
    score = evaluate_grounding(findings, evidence)
    assert score < 1.0  # Penalized for ungrounded claim
    assert score > 0.5  # But not zero

def test_citation_quality():
    """Test citation format and relevance."""
    report = {"findings": [...], "evidence": [...], "sources": [...]}
    score = evaluate_citations(report)
    assert score >= 0.8  # Minimum threshold
```

## Test Configuration

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from packages.database.connection import Base

@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine):
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()
```

## Running Tests

```bash
# Backend unit tests
cd apps/api && pytest tests/unit -v

# Backend integration tests (requires Docker services)
cd apps/api && pytest tests/integration -v

# Frontend unit tests
cd apps/web && npm run test:unit

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=packages --cov=apps/api/src --cov-report=html
```

## CI Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: cd apps/api && pip install -e ".[test]"
      - run: cd apps/api && pytest tests/unit --cov

  backend-integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: {POSTGRES_DB: test, POSTGRES_PASSWORD: test}
        ports: [5432:5432]
      chroma:
        image: chromadb/chroma:latest
        ports: [8000:8000]
      redis:
        image: redis:7
        ports: [6379:6379]
    steps:
      - uses: actions/checkout@v4
      - run: cd apps/api && pytest tests/integration

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '20'}
      - run: cd apps/web && npm ci
      - run: cd apps/web && npm run test:unit
      - run: cd apps/web && npm run lint
```

---

*Tests should run fast and reliably without external dependencies. Use mocks liberally.*