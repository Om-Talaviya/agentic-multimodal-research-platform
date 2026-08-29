"""Tests for document upload API route and ingestion integration."""

import io
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import ASGITransport, AsyncClient
from main import app
from database.models import Document
from database.connection import get_session
from api.routes.documents import get_model_gateway


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


@pytest.fixture
def mock_document_repo():
    repo = MagicMock()
    created_docs = {}

    async def mock_create(doc):
        created_docs[doc.id] = doc
        return doc

    async def mock_get(doc_id):
        return created_docs.get(doc_id)

    async def mock_create_chunks(chunks):
        return chunks

    repo.create = AsyncMock(side_effect=mock_create)
    repo.get = AsyncMock(side_effect=mock_get)
    repo.create_chunks = AsyncMock(side_effect=mock_create_chunks)
    return repo


@pytest.mark.asyncio
async def test_upload_document_success(mock_document_repo, mock_db_session):
    async def override_get_session():
        yield mock_db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_model_gateway] = lambda: None

    with patch("api.routes.documents.DocumentRepository", return_value=mock_document_repo):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            file_content = b"# Introduction\n\nThis is a research document about multimodal AI.\n\nSection 2."
            files = {"file": ("research_paper.md", io.BytesIO(file_content), "text/markdown")}
            data = {"research_job_id": "11111111-1111-1111-1111-111111111111"}

            response = await client.post("/api/v1/documents", files=files, data=data)

    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "research_paper.md"
    assert data["mime_type"] == "text/markdown"
    assert data["status"] == "ingested"
    assert "id" in data
    assert mock_document_repo.create.await_count == 1
    assert mock_document_repo.create_chunks.await_count == 1


@pytest.mark.asyncio
async def test_upload_document_invalid_extension(mock_db_session):
    async def override_get_session():
        yield mock_db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        file_content = b"executable code"
        files = {"file": ("script.exe", io.BytesIO(file_content), "application/octet-stream")}

        response = await client.post("/api/v1/documents", files=files)

    app.dependency_overrides.clear()

    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_get_document_success(mock_document_repo, mock_db_session):
    from uuid import uuid4
    from datetime import datetime

    test_id = uuid4()
    mock_doc = Document(
        id=test_id,
        filename="test.txt",
        mime_type="text/plain",
        file_size=100,
        file_path="/tmp/test.txt",
        created_at=datetime.utcnow(),
    )
    mock_document_repo.get.side_effect = None
    mock_document_repo.get.return_value = mock_doc

    async def override_get_session():
        yield mock_db_session

    app.dependency_overrides[get_session] = override_get_session

    with patch("api.routes.documents.DocumentRepository", return_value=mock_document_repo):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/documents/{test_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_id)
    assert data["filename"] == "test.txt"
    assert data["status"] == "ingested"
