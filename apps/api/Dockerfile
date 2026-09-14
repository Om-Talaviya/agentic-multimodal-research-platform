# ==============================================================================
# Production Dockerfile for Agentic Multimodal Research Platform API (Backend)
# Multi-stage lightweight distroless/slim Python 3.11 build
# ==============================================================================

FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy monorepo package definitions
COPY pyproject.toml /build/
COPY packages/ /build/packages/
COPY apps/api/ /build/apps/api/

# Install python dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic \
    pydantic-settings \
    sqlalchemy[asyncio] \
    asyncpg \
    aiosqlite \
    structlog \
    python-jose[cryptography] \
    httpx \
    numpy \
    scipy \
    rank-bm25 \
    chromadb \
    pdfplumber \
    python-docx \
    pillow

# Install local monorepo packages in editable mode
RUN pip install -e /build/packages/shared && \
    pip install -e /build/packages/database && \
    pip install -e /build/packages/ai && \
    pip install -e /build/packages/tools && \
    pip install -e /build/packages/ingestion && \
    pip install -e /build/packages/retrieval && \
    pip install -e /build/packages/research && \
    pip install -e /build/packages/agents && \
    pip install -e /build/apps/api

# ==============================================================================
# Final Runner Stage
# ==============================================================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Install runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv and code from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/api/src:/app/packages/shared/src:/app/packages/database/src:/app/packages/ai/src:/app/packages/tools/src:/app/packages/ingestion/src:/app/packages/retrieval/src:/app/packages/research/src:/app/packages/agents/src"
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1001 researchuser && \
    chown -R researchuser:researchuser /app

USER researchuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

WORKDIR /app/apps/api

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
