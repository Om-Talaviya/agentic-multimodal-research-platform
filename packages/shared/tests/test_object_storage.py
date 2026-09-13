"""Unit tests for S3/MinIO/Local ObjectStorageClient (Phase 24)."""
import os
import shutil
import tempfile
import pytest
from shared.storage import ObjectStorageClient

@pytest.fixture
def temp_storage():
    temp_dir = tempfile.mkdtemp()
    client = ObjectStorageClient(base_storage_dir=temp_dir, default_bucket="test-bucket")
    yield client, temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_put_get_delete_object(temp_storage):
    client, _ = temp_storage
    content = b"Multimodal Research Report PDF Binary Content 12345"
    key = "reports/report-2026-09-13.pdf"

    # Put object
    res = client.put_object(
        object_key=key,
        data=content,
        content_type="application/pdf",
        metadata={"author": "Alice"},
    )
    assert res["object_key"] == key
    assert res["bucket"] == "test-bucket"
    assert res["size_bytes"] == len(content)
    assert res["content_type"] == "application/pdf"
    assert res["md5_hash"] is not None

    # Get object
    retrieved = client.get_object(object_key=key)
    assert retrieved == content

    # Metrics
    metrics = client.get_bucket_metrics("test-bucket")
    assert metrics["total_objects"] == 1
    assert metrics["total_size_bytes"] == len(content)

    # Delete object
    deleted = client.delete_object(object_key=key)
    assert deleted is True

    with pytest.raises(FileNotFoundError):
        client.get_object(object_key=key)

def test_presigned_url_generation(temp_storage):
    client, _ = temp_storage
    url_res = client.generate_presigned_url(
        object_key="datasets/genomics.csv",
        operation="get_object",
        expires_in_seconds=1800,
    )
    assert "url" in url_res
    assert "auth_token=" in url_res["url"]
    assert url_res["object_key"] == "datasets/genomics.csv"
    assert url_res["expires_in_seconds"] == 1800
