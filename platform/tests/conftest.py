"""
Pytest configuration and fixtures for integration tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../services/api-gateway/src"))

from main import app


@pytest.fixture
def api_client():
    """Create test client for API Gateway."""
    return TestClient(app)


@pytest.fixture
def sample_connection_request():
    """Sample model connection request for testing."""
    return {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "sk-test123456789",
        "name": "Test GPT-3.5 Model",
        "config": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }


@pytest.fixture
def mock_openai_connector():
    """Mock OpenAI connector for testing."""
    mock_connector = Mock()
    mock_connector.test_connection = AsyncMock(return_value=Mock(
        status=Mock(value="success"),
        message="Connection successful",
        latency_ms=245.5,
        model_info={"model": "gpt-3.5-turbo", "provider": "openai"}
    ))
    return mock_connector


@pytest.fixture
def mock_storage_operations():
    """Mock storage operations for testing."""
    mock_cred_storage = Mock()
    mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
        status=Mock(value="success"),
        message="Credentials stored successfully"
    ))
    
    mock_meta_storage = Mock()
    mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
        status=Mock(value="success"),
        message="Metadata stored successfully"
    ))
    mock_meta_storage.list_user_models = AsyncMock(return_value=Mock(
        status=Mock(value="success"),
        message="Found models for user",
        data={"models": []}
    ))
    
    return mock_cred_storage, mock_meta_storage


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

