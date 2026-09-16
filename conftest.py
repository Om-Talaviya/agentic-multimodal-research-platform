"""Pytest root configuration and global model registration fixture."""

import pytest
import database.models  # Pre-registers all database tables into Base.metadata
from database.connection import Base

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure all model definitions are loaded into Base metadata."""
    assert len(Base.metadata.tables) > 0, "No tables discovered in Base.metadata"
