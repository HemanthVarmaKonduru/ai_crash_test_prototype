"""
Pytest configuration and fixtures for storage tests.
"""

import pytest
from cryptography.fernet import Fernet
from src.credential_storage import CredentialStorage
from src.model_metadata import ModelMetadataStorage


@pytest.fixture
def encryption_key():
    """Generate a test encryption key."""
    return Fernet.generate_key().decode()


@pytest.fixture
def credential_storage(encryption_key):
    """Create CredentialStorage instance for testing."""
    return CredentialStorage(encryption_key)


@pytest.fixture
def metadata_storage():
    """Create ModelMetadataStorage instance for testing."""
    return ModelMetadataStorage()


@pytest.fixture
def sample_credentials():
    """Sample credentials for testing."""
    return {
        "api_key": "sk-test123456789",
        "model": "gpt-3.5-turbo",
        "provider": "openai"
    }


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "model_id": "user123:openai:gpt-3.5-turbo",
        "user_id": "user123",
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "name": "Test GPT-3.5 Model",
        "status": "connected",
        "latency_ms": 245.5,
        "config": {"temperature": 0.7}
    }

