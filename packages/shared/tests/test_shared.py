"""Tests for shared package."""

import pytest
from shared.config import Settings
from shared.exceptions import (
    ResearchError, ValidationError, NotFoundError, ProviderError,
    AgentError, RateLimitError, PlanningError,
)
from shared.types import TaskStatus, JobStatus, DocumentFormat, VerificationStatus


def test_settings_defaults():
    """Test settings have correct defaults."""
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        secret_key="test-secret",
    )
    
    assert settings.app_name == "Agentic Multimodal Research Platform"
    assert settings.api_port == 8000
    assert settings.log_level == "INFO"
    assert settings.max_upload_size == 50 * 1024 * 1024


def test_research_error():
    """Test ResearchError base class."""
    error = ResearchError("Test error", code="TEST_CODE", details={"key": "value"})
    
    assert str(error) == "Test error"
    assert error.code == "TEST_CODE"
    assert error.details == {"key": "value"}
    assert error.to_dict() == {
        "error": {"code": "TEST_CODE", "message": "Test error", "details": {"key": "value"}}
    }


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid input", field="email", details={"reason": "format"})
    
    assert error.code == "VALIDATION_ERROR"
    assert error.details["field"] == "email"
    assert error.details["reason"] == "format"


def test_not_found_error():
    """Test NotFoundError."""
    error = NotFoundError("ResearchJob", "123")
    
    assert error.code == "NOT_FOUND"
    assert "ResearchJob not found: 123" in str(error)
    assert error.details["resource"] == "ResearchJob"
    assert error.details["identifier"] == "123"


def test_provider_error():
    """Test ProviderError."""
    error = ProviderError("ollama", "Connection refused")
    
    assert error.code == "PROVIDER_ERROR"
    assert "ollama" in str(error)
    assert error.details["provider"] == "ollama"


def test_agent_error():
    """Test AgentError."""
    error = AgentError("planner", "Failed to create plan")
    
    assert error.code == "AGENT_ERROR"
    assert "planner" in str(error)
    assert error.details["agent"] == "planner"


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError(60, 60)
    
    assert error.code == "RATE_LIMITED"
    assert "60 requests per 60 seconds" in str(error)
    assert error.details["limit"] == 60
    assert error.details["window_seconds"] == 60


def test_planning_error():
    """Test PlanningError."""
    error = PlanningError("Invalid plan structure")
    
    assert error.code == "PLANNING_ERROR"
    assert "Invalid plan structure" in str(error)


def test_task_status_enum():
    """Test TaskStatus enum values."""
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.RUNNING == "running"
    assert TaskStatus.COMPLETED == "completed"
    assert TaskStatus.FAILED == "failed"


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.PENDING == "pending"
    assert JobStatus.RUNNING == "running"
    assert JobStatus.COMPLETED == "completed"
    assert JobStatus.FAILED == "failed"
    assert JobStatus.CANCELLED == "cancelled"


def test_document_format_enum():
    """Test DocumentFormat enum values."""
    assert DocumentFormat.TEXT == "text"
    assert DocumentFormat.PDF == "pdf"
    assert DocumentFormat.DOCX == "docx"
    assert DocumentFormat.IMAGE == "image"
    assert DocumentFormat.UNKNOWN == "unknown"


def test_verification_status_enum():
    """Test VerificationStatus enum values."""
    assert VerificationStatus.UNVERIFIED == "unverified"
    assert VerificationStatus.SINGLE_SOURCE == "single_source"
    assert VerificationStatus.CONSENSUS == "consensus"
    assert VerificationStatus.CONFLICT == "conflict"
    assert VerificationStatus.PARTIAL == "partial"